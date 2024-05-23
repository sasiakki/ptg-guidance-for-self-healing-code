#https://seiu775bg.atlassian.net/browse/DT-824
#Remove Smartsheet Course Completions from E2E Process
'''
import sys
import boto3
import json
import pandas
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col,current_date,concat,rank,when,lit,to_date,date_format,when,current_timestamp
from awsglue.dynamicframe import DynamicFrame
from datetime import datetime,date
from pyspark.sql.functions import *
from pyspark.sql.types import LongType


args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'
    
#Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

#Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3'
)

s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Setting the timeParserPolicy as legacy for handling multiple types of date formats received in smartsheet_course_completion responses  
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

#Capturing the current date to append to filename
today = datetime.now()
suffix = today.strftime("%m_%d_%y")

print("****************Starting Job execution*******************")
#Smartsheet course completions table with only delta records
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_raw_ss_course_completion",
).toDF().filter("isdelta == 'true'").createOrReplaceTempView("raw_ss_course_completions")

#Script for node PostgreSQL of coursecatalog
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_coursecatalog",
).toDF().filter("status == 'Active'").createOrReplaceTempView("coursecatalog")

# Script generated for node PostgreSQL
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_prod_person",).toDF().createOrReplaceTempView("person")
# Script for node PostgreSQL of instructor
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name= catalog_table_prefix+"_prod_instructor",
).toDF().createOrReplaceTempView("instructor")

# Removing the duplicate course completions received from multiple sheets and only preserving completions in the earliest sheet date
spark.sql("with ss_raw as (select  sc.learner_id ,sc.class_title,sc.attendance,sc.date,sc.class_id,sc.instructor,sc.learner_email,sc.first_name,sc.last_name ,to_date(element_at(split(sc.sheet_name, '-'),2),'yyyyMMdd') as sheetdate, sc.filename,sc.filedate, ROW_NUMBER () OVER ( PARTITION BY sc.learner_id, sc.class_title ORDER BY to_date(element_at(split(sc.sheet_name, '-'),2),'yyyyMMdd') DESC, sc.date ASC ) courserank from raw_ss_course_completions sc  where sc.attendance = 'Attended'  order by sc.class_title desc, sc.date) select * from ss_raw where  courserank = 1").createOrReplaceTempView("raw_ss_course_completions")

# Removing duplicate courses, if the course is offered in both online(ONL) and also Instructor-Led (ILT) the we pick the ILT courseid as default
spark.sql("with coursecatalog as (select *, ROW_NUMBER () OVER ( PARTITION BY curr.coursename, curr.courselanguage,curr.trainingprogramcode ORDER BY curr.coursetype ASC ) courserank from coursecatalog curr) select  coursename ,credithours ,trainingprogramtype, trainingprogramcode, coursetype, courselanguage,courseversion,courseid,dshscourseid from coursecatalog where courserank = 1").createOrReplaceTempView("coursecatalog")

# Capturing only the active instuctors from the instructor table
spark.sql("select distinct trim(concat(trim(firstname),' ',trim(lastname))) as instructorname , dshsinstructorid  as instructorid from instructor where isactive = 'true'").createOrReplaceTempView("instructor")

## Identify and flagging valid and invalid records if personid not found in prod person table
spark.sql("""select cs.*, 
                CASE WHEN pr.personid is null or cast(cs.date as DATE) > current_date THEN 0 ELSE 1 END ValidInd,
                CASE 
                 WHEN pr.personid is null THEN 'personid is not Valid'
                 WHEN cast(cs.date as DATE) > current_date THEN 'Completion Date is in the Future'
             END ValidIndERR
          from raw_ss_course_completions cs left join person pr on trim(cs.learner_id) = cast(pr.personid as string)""").createOrReplaceTempView("raw_ss_course_completions_completionLastName_instructor_email_valid_flag")
          
## identifying duplicate records based on learner_id,class_title getting earliest record and flagging valid and invalid records
spark.sql("select date,learner_id,class_id,last_name,learner_email,class_title,first_name,instructor,filename,filedate,\
            CASE WHEN completionsrank>1 then 'Course Completion is Redundant' end as ValidIndERR, \
            CASE WHEN completionsrank>1 then 0 else 1 end as ValidInd \
            from (select *, row_number() over (Partition by learner_id,class_title ORDER BY  date ASC ) completionsrank \
            from  raw_ss_course_completions_completionLastName_instructor_email_valid_flag where ValidInd=1) DS").createOrReplaceTempView("raw_ss_course_completions_DuplicateCourseError")
            
## Filtering invalid class_title and flagging valid and invalid records
spark.sql("""select date,learner_id,class_id,last_name,learner_email,class_title,learner_email,first_name,instructor,filename,filedate,
                        CASE
                        WHEN tc.coursename is null then 'CourseID is not Valid'
                        WHEN ins.instructorname is null then 'Instructorname is not Valid' end as ValidIndERR, 
                        CASE WHEN tc.coursename is null or ins.instructorname is null then 0 else 1 end as ValidInd 
                       from raw_ss_course_completions_DuplicateCourseError cs 
                       left join coursecatalog tc on lower(trim(cs.class_title)) = lower(concat(trim(tc.coursename),' ',tc.courselanguage))
                       left join instructor ins on lower(trim(ins.instructorname)) = lower(trim(cs.instructor)) where cs.ValidInd=1""").createOrReplaceTempView("raw_ss_course_completions_DuplicateError")

                
                      
#Combining duplicate records 
finalInvalidDF = spark.sql("""select learner_id,class_title,class_id,date,last_name,first_name,learner_email,instructor,filename,filedate,ValidInd,ValidIndERR from
                                raw_ss_course_completions_completionLastName_instructor_email_valid_flag where ValidInd=0  
                            UNION 
                            select learner_id,class_title,class_id,date,last_name,first_name,
                            learner_email,instructor,filename,filedate,ValidInd,ValidIndERR from 
                            raw_ss_course_completions_DuplicateError where ValidInd = 0
                            UNION 
                            select learner_id,class_title,class_id,date,last_name,first_name,learner_email,instructor,filename,filedate,ValidInd,ValidIndERR from 
                            raw_ss_course_completions_DuplicateCourseError where ValidInd = 0 """)
                            
# Combining coursecatalog , instructor and completion details   
sscompletionsdf = spark.sql("select distinct sc.learner_id ,sc.class_title ,sc.date as completiondate ,tc.credithours,tc.trainingprogramtype,tc.trainingprogramcode ,tc.courseid ,tc.coursetype ,tc.courselanguage ,tc.dshscourseid, sc.instructor as instructorname,ins.instructorid,sc.filedate,sc.filename,'SMARTSHEET' as trainingsource from raw_ss_course_completions sc left join coursecatalog tc on lower(trim(sc.class_title)) = lower(concat(trim(tc.coursename),' ',tc.courselanguage)) left join instructor ins on lower(trim(ins.instructorname)) = lower(trim(sc.instructor))")

# Coverting  spark dataframe to glue dynamic dataframe
newdatasource = DynamicFrame.fromDF(sscompletionsdf, glueContext, "newdatasource")

# Script generated for node Apply Mapping
ApplyMapping_node1646956720451 = ApplyMapping.apply(
    frame= newdatasource,
    mappings=[
        ("learner_id", "string", "personid", "long"),
        ("class_title", "string", "coursename", "string"),
        ("completiondate", "date", "completeddate", "date"),
        ("credithours", "string", "credithours", "double"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "long"),
        ("courseid", "string", "courseid", "string"),
        ("coursetype", "string", "coursetype", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("instructorid", "string", "instructorid", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
         ("filedate", "date", "filedate", "timestamp"),
         ("filename", "string", "filename", "string"),
          ("dshscourseid", "string", "dshscourseid", "string"),
    ],
    transformation_ctx="ApplyMapping_node1646956720451",
)
selectFields_raw_trainghistory = SelectFields.apply(
    frame=ApplyMapping_node1646956720451,
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
        "filedate",
        "filename",
        "dshscourseid"
    ],
    transformation_ctx="b2bdevdb_raw_traininghistory",
)
dyf_dropNullfields = DropNullFields.apply(frame = selectFields_raw_trainghistory)

#Script for node PostgreSQL writing to raw.traininghistory
glueContext.write_dynamic_frame.from_catalog(
    frame=dyf_dropNullfields,
    database = catalog_database,
    table_name= catalog_table_prefix+"_raw_traininghistory",
)
#If invalid records found 

if(finalInvalidDF.count() > 0):
    print("Found Invalid records")
    ## used to generate csv file invalid records from source file into s3 outbound folder
    outboundDF = finalInvalidDF.withColumnRenamed("date","Completion Date")\
                        .withColumnRenamed("learner_id","Learner ID")\
                        .withColumnRenamed("class_id","Class ID")\
                        .withColumnRenamed("last_name","Last Name")\
                        .withColumnRenamed("class_title","Class Title")\
                        .withColumnRenamed("learner_email","Learner Email")\
                        .withColumnRenamed("ValidIndERR","Error Reason")\
                        .withColumnRenamed("first_name","First Name")\
                        .drop(col("ValidInd"))


    pandas_df = outboundDF.toPandas()

    today = date.today()
    suffix = today.strftime("%Y-%m-%d")
    pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/smartsheet_course_completion/smartsheet_raw_traininghistory_errorlog-"+suffix+".csv",header=True, index=None, sep=',')    
    print(suffix)
    print ("Invalid records: {0}".format(finalInvalidDF.count()))

    # Adding to traininghistory logs
    finalInvalidDF.createOrReplaceTempView("finalInvalidDF")
    errordf = spark.sql("select cast(learner_id as bigint) personid, class_title as coursename, cast(date as date) completeddate, filename, filedate,instructor as instructorname,'SMARTSHEET' as trainingsource,ValidIndERR as error_message from finalInvalidDF")
    errorcdf = DynamicFrame.fromDF(errordf, glueContext, "historydf")

    glueContext.write_dynamic_frame.from_catalog(
    frame = errorcdf,
    database = catalog_database,
    table_name = catalog_table_prefix+"_logs_traininghistorylog",
    )
print("****************Job execution completed*******************")
job.commit()

'''