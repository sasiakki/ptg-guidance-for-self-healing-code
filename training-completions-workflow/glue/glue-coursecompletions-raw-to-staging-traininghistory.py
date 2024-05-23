import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import pandas
from datetime import datetime
import boto3
import json
import csv

# Default Job Arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'


# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'') 

# Script for node PostgreSQL table raw_traininghistory
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name= catalog_table_prefix+"_raw_traininghistory",
).toDF().createOrReplaceTempView("traininghistory")

# Script for node PostgreSQL prod_transcript
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_transcript",
).toDF().createOrReplaceTempView("transcript")

# Script for node PostgreSQL prod_trainingrequirement
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_trainingrequirement",
).toDF().createOrReplaceTempView("trainingrequirement")

# Script for node PostgreSQL prod_courseequivalency
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_courseequivalency",
).toDF().createOrReplaceTempView("courseequivalency")

#Capturing active training requirements only when the tracking date is not an future date and only by earliest trackingdate
spark.sql("""
     select * from (
        select 
            COALESCE(requiredhours,0) as requiredhours
            ,COALESCE(earnedhours, 0) as earnedhours
            ,transferredhours
            ,trainingprogram
            ,cast(trainingprogramcode as bigint) as trainingprogramcode
            ,status
            ,trainingid
            ,trainreq_id
            ,completeddate
            ,isrequired
            ,trackingdate
            ,duedate
            ,isoverride
            ,duedateextension
            ,created
            ,personid
            ,learningpath
            ,recordcreateddate
            ,ROW_NUMBER() OVER ( PARTITION BY personid,trainingprogramcode  ORDER BY cast(trackingdate as date) ASC) training_rank_by_createddate
        from trainingrequirement where lower(status) != 'closed'
            and cast(trackingdate as date) <= current_date order by personid ,trainingprogramcode) as trainings
    where training_rank_by_createddate  = 1
          """).createOrReplaceTempView("trainingrequirement")

#Join traininghistory with course equivalency to check for multiple learning paths and determine the one to many releationship
#Learing Paths are applicable only to BT Training programs 
spark.sql("""
          select distinct 
                rth.personid
                ,rth.courseid
               ,coalesce(cast(pce.trainingprogramcode as bigint), rth.trainingprogramcode) as trainingprogramcode
                ,coalesce(pce.trainingprogramtype,rth.trainingprogramtype) as trainingprogramtype
                ,pce.learningpath from  traininghistory rth 
            join courseequivalency pce on rth.courseid = pce.courseid
          """).createOrReplaceTempView("equivalenttraininghistory")

# Join equivalent traininghistory with the personid active training requirement  to propage many to one releationship
# Evaluating person has changed the learning path or not on below conditions
# 1. Training Requirement is not associated with any learning path and earnedhours is 0 then it is not change in learning path, as person has started learning path 
# 2. Training Requirement is associated with an specific learning path and new completions received for an different learning path, then it is change in learning path
spark.sql("""
          select  
     rth.personid
    ,rth.courseid
    ,rth.learningpath
    ,ptr.learningpath as oldlearningpath
    ,rth.trainingprogramcode
    ,rth.trainingprogramtype
    ,ptr.trainingid
    , case when ptr.learningpath is null and coalesce(ptr.earnedhours,0) = 0 then false 
           when coalesce (rth.learningpath,rth.trainingprogramcode) <> coalesce(ptr.learningpath,ptr.trainingprogramcode) then true 
           else false end as islearningpathchanged
    from equivalenttraininghistory rth join trainingrequirement ptr on rth.personid = ptr.personid and  rth.trainingprogramcode = ptr.trainingprogramcode 
where ptr.status = 'active'
          """).createOrReplaceTempView("equivalenttraings")

# Join  equivalent trainings with raw completions to determine equivalent trainingprogram based on courseid and personid
# and evaluating person has any  active trainingrequirement
spark.sql("""
          select
    rth.personid
    ,rth.coursename
    ,rth.courseid
    ,rth.completeddate
    ,rth.credithours
    ,coalesce(cast(eqt.trainingprogramcode as bigint), rth.trainingprogramcode) as trainingprogramcode
    ,coalesce(eqt.trainingprogramtype,rth.trainingprogramtype) as trainingprogramtype
    ,rth.courselanguage
    ,rth.coursetype
    ,rth.instructorname
    ,rth.instructorid
    ,rth.trainingsource
    ,rth.dshscourseid
    ,rth.dshsid
    ,rth.qual_person_id
    ,eqt.learningpath
    ,eqt.oldlearningpath
    ,eqt.islearningpathchanged
    ,rth.filename
    ,to_date(rth.filedate) as filedate
    ,case when eqt.trainingid  is not null then true else false end as hasactivetrainingrequirement
from equivalenttraings eqt right join traininghistory rth on rth.personid = eqt.personid and rth.courseid = eqt.courseid          
          """).createOrReplaceTempView("traininghistory")

# Capturing the duplicates in join with transcript table to calcualted traininghistory
spark.sql(""" select distinct rth.*,case when ptp.courseid is not null then true else false end as isduplicatecompletion
          ,RANK () OVER ( PARTITION BY rth.personid, concat(LEFT(rth.courseid,7),RIGHT(rth.courseid, 2)) ORDER BY rth.completeddate ASC ) courserank
    from traininghistory rth left join transcript ptp 
    on  rth.personid = ptp.personid and concat(LEFT(rth.courseid,7),RIGHT(rth.courseid, 2)) = concat(LEFT(ptp.courseid,7),RIGHT(ptp.courseid, 2))
    """).createOrReplaceTempView("r_traininghistory")

#Determining a completion as unique based on 
# 1. Not Previously completed 
# 2. coursetitle is mapped accurately with courseid, and credit hours  
# 3. this check for agency completions as personid should be vaild
uniquiecompletions = spark.sql(""" select * from r_traininghistory  where isduplicatecompletion = 'false' and  courseid is not null and courserank = 1 and 
                                    personid is not null and completeddate is not null""")\
                    .selectExpr( "oldlearningpath","learningpath","islearningpathchanged","personid","completeddate","credithours","coursename","courseid","coursetype","courselanguage","trainingprogramcode","trainingprogramtype","instructorname","instructorid","trainingsource","dshscourseid","filename","filedate").distinct()

allduplicates = spark.sql(""" select *, 
                case 
                    when completeddate is null then 'Completion Date is not Valid'
                    when courseid is null then 'CourseID is not Valid'  
                    when isduplicatecompletion = 'true' then 'Course was previously Completed'
                    when courserank > 1 then 'Course Completion is Redundant'
                    when personid is null then 'PersonID is not Valid'
                    end as error_message 
                from r_traininghistory  where isduplicatecompletion = 'true' or courseid is null or courserank > 1 or personid is null or completeddate is null""")\
                    .selectExpr("personid","completeddate","credithours","coursename","courseid","coursetype","courselanguage","trainingprogramcode","trainingprogramtype","instructorname","instructorid","trainingsource","dshsid","qual_person_id","dshscourseid","filename","filedate","error_message")

print ("Valid records: {0}".format(uniquiecompletions.count()))
# Coverting  spark dataframe to glue dynamic dataframe
uniquiecompletionsdatasource = DynamicFrame.fromDF(uniquiecompletions, glueContext, "uniquiecompletionsdatasource")

# ApplyMapping to match the target table
ApplyMapping_uniquiecompletions = ApplyMapping.apply(
    frame=uniquiecompletionsdatasource,
    mappings=[
        ("islearningpathchanged", "boolean", "islearningpathchanged", "boolean"),
        ("learningpath", "string", "learningpath", "string"),
        ("coursename", "string", "coursename", "string"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("coursetype", "string", "coursetype", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("trainingprogramcode", "long", "trainingprogramcode", "long"),
        ("personid", "long", "personid", "long"),
        ("completeddate", "date", "completeddate", "date"),
        ("courseid", "string", "courseid", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("credithours", "double", "credithours", "double"),
        ("instructorid", "string", "instructorid", "string"),
        ("dshscourseid", "string", "dshscourseid", "string"),
        ("filename", "string", "filename", "string"),
        ("filedate", "date", "filedate", "date")
    ],
    transformation_ctx="ApplyMapping_uniquiecompletions",
)

selectFields_staging_trainghistory = SelectFields.apply(
    frame=ApplyMapping_uniquiecompletions,
    paths=[
        "islearningpathchanged",
        "learningpath",
        "personid",
        "completeddate",
        "credithours",
        "coursename",
        "courseid",
        "coursetype",
        "courselanguage",
        "trainingprogramcode",
        "trainingprogramtype",
        "instructorname",
        "instructorid",
        "trainingsource",
        "dshscourseid",
        "filename",
        "filedate"
    ],
    transformation_ctx="selectFields_staging_trainghistory",
)

uniquiecompletions_dropNullfields = DropNullFields.apply(frame = selectFields_staging_trainghistory)

# Script for node PostgreSQL to push to staging.traininghistory
glueContext.write_dynamic_frame.from_catalog(
    frame=uniquiecompletions_dropNullfields,
    database = catalog_database,
    table_name=catalog_table_prefix+"_staging_traininghistory"
)

if(allduplicates.count() > 0):
    suffix = str(datetime.now().strftime("%Y-%m-%d_%H%M"))
    pandas_df = allduplicates.toPandas()
    pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/duplicates/raw_traininghistory_to_staging_error_"+suffix +".csv", header = True, index = None, quotechar= '"', encoding ='utf-8', sep =',',quoting = csv.QUOTE_ALL)
    print(suffix)
    print ("Invalid records: {0}".format(allduplicates.count()))

# Coverting  spark dataframe to glue dynamic dataframe
duplicatecompletionsdatasource = DynamicFrame.fromDF(allduplicates, glueContext, "duplicatecompletionsdatasource")

# ApplyMapping to match the target table
ApplyMapping_duplicatecompletionsandpersonidnulldatasource = ApplyMapping.apply(
    frame=duplicatecompletionsdatasource,
    mappings=[
        ("recordcreateddate", "timestamp", "recordcreateddate", "timestamp"),
        ("coursename", "string", "coursename", "string"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("coursetype", "string", "coursetype", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("trainingprogramcode", "long", "trainingprogramcode", "long"),
        ("personid", "long", "personid", "long"),
        ("qual_person_id", "long", "qual_person_id", "long"),
        ("completeddate", "date", "completeddate", "date"),
        ("courseid", "string", "courseid", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("credithours", "double", "credithours", "double"),
        ("instructorid", "string", "instructorid", "string"),
        ("dshsid", "long", "dshsid", "long"),
        ("dshscourseid", "string", "dshscourseid", "string"),
        ("filename", "string", "filename", "string"),
        ("filedate", "date", "filedate", "date"),
        ("error_message", "string", "error_message", "string"),
    ],
    transformation_ctx="ApplyMapping_duplicatecompletionsandpersonidnulldatasource",
)

selectFields_log_trainghistorylog = SelectFields.apply(
    frame=ApplyMapping_duplicatecompletionsandpersonidnulldatasource,
    paths=[
        "personid",
        "completeddate",
        "credithours",
        "coursename",
        "courseid",
        "coursetype",
        "courselanguage",
        "trainingprogramcode",
        "trainingprogramtype",
        "instructorname",
        "instructorid",
        "trainingsource",
        "dshsid",
        "qual_person_id",
        "dshscourseid",
        "filename",
        "filedate",
        "error_message"
    ],
    transformation_ctx="selectFields_log_trainghistorylog",
)

duplicatecompletionsandpersonidnulldatasource_dropNullfields = DropNullFields.apply(frame = selectFields_log_trainghistorylog)

# Script for node PostgreSQL to push to logs.traininghistorylog
glueContext.write_dynamic_frame.from_catalog(
    frame=duplicatecompletionsandpersonidnulldatasource_dropNullfields,
    database= catalog_database,
    table_name= catalog_table_prefix+"_logs_traininghistorylog"
)

job.commit()