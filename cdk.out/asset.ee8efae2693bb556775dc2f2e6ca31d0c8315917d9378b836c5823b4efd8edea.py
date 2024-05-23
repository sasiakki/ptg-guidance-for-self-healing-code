import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
import pandas
from datetime import datetime
import boto3
import json
import csv

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

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/rds/system-pipelines'
)
database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print("****************Starting Job execution*******************")
# Script generated for node PostgreSQL table
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_raw_cornerstone_completion",
    transformation_ctx = "raw_cornerstone_completion",
).toDF().createOrReplaceTempView("raw_cs_cornerstone_completion")

# Script generated for node PostgreSQL
prodpersondf = glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_prod_person",
).toDF()

#Removing blank spaces for all columns
prodpersondf = prodpersondf.select([when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c) for c in prodpersondf.columns])

prodpersondf.createOrReplaceTempView("prodperson")
    
# Script generated for node PostgreSQL
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_coursecatalog",
).toDF().createOrReplaceTempView("coursecatalog")

#Capturing lastprocessed datetime from logs.lastprocessed
## B2BDS-1340: Access the lastprocessed log table and create a DF for Delta Detection purpose
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, 
    table_name=catalog_table_prefix+"_logs_lastprocessed"
 ).toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")

# Renaming the columns and filtering results with status as Passed
raw_cs_cornerstone_completion_df = spark.sql("""   select trim(bg_person_id) as learner_id
                     , case when trim(offering_title) = 'Establishing Trust Through Communication with the Elderly 2h' then 'Establishing Trust Through Communication with the Elderly'
                            when trim(offering_title) = 'Basic Training 30  (30 hrs)' then 'Basic Care for Individual Providers (30 hrs)' 
                            else trim(substring_index(trim(offering_title),'(',1)) end as class_title
                     , trim(course_title) as class_id
                     , cast(from_utc_timestamp(completion_date,'America/Los_Angeles') as date) date
                     , trim(user_last_name) as last_name
                     , trim(user_first_name) as first_name
                     , trim(user_email) as learner_email
                     , filename
                     , filedate
                     from raw_cs_cornerstone_completion where status = 'Passed' AND recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-cornerstone-completions-raw-to-raw-traininghistory' AND success='1')""")

if (raw_cs_cornerstone_completion_df.count() > 0):   
    raw_cs_cornerstone_completion_df.createOrReplaceTempView("raw_cs_cornerstone_completion")

    print ("Total records from raw : {0}".format(raw_cs_cornerstone_completion_df.count()))

    ## Removing duplicate courses, if the course is offered in both online(ONL) and also Instructor-Led (ILT) the we pick the ILT courseid as default
    spark.sql("with coursecatalog as (select *, ROW_NUMBER () OVER ( PARTITION BY curr.coursename, curr.courselanguage,curr.trainingprogramcode ORDER BY curr.coursetype ASC ) courserank \
                from coursecatalog curr where curr.coursetype ='ONL') select  coursename ,credithours ,trainingprogramtype, trainingprogramcode, coursetype, courselanguage,courseversion,courseid,dshscourseid from coursecatalog where courserank = 1").createOrReplaceTempView("coursecatalog")

    ## Identify and flagging valid and invalid records if personid not found in prod person table
    spark.sql("""select cs.*, 
                    CASE WHEN pr.personid is null or cast(cs.date as DATE) > current_date THEN 0 ELSE 1 END ValidInd,
                    CASE 
                     WHEN pr.personid is null THEN 'PersonID is not Valid'
                     WHEN cast(cs.date as DATE) > current_date THEN 'Completion Date is in the Future'
                 END ValidIndERR
              from raw_cs_cornerstone_completion cs left join prodperson pr on trim(cs.learner_id) = cast(pr.personid as string)""").createOrReplaceTempView("raw_cs_cornerstone_completionLastName_person_email_valid_flag")


    ## identifying duplicate records based on learner_id,class_title getting earliest record and flagging valid and invalid records
    spark.sql("select date,learner_id,class_id,last_name,class_title,learner_email,filename,filedate,first_name,\
                CASE WHEN completionsrank>1 then 'Course Completion is Redundant' end as ValidIndERR, \
                CASE WHEN completionsrank>1 then 0 else 1 end as ValidInd \
                from (select *, row_number() over (Partition by learner_id,class_title ORDER BY  date ASC ) completionsrank \
                from  raw_cs_cornerstone_completionLastName_person_email_valid_flag where ValidInd=1) DS").createOrReplaceTempView("raw_cs_cornerstone_DuplicateCourseError")

    ## Filtering invalid class_title and flagging valid and invalid records
    spark.sql("select date,learner_id,class_id,last_name,class_title,learner_email,filename,filedate,first_name,\
                            CASE WHEN tc.coursename is null then 'CourseID is not Valid' end as ValidIndERR, \
                            CASE WHEN tc.coursename is null then 0 else 1 end as ValidInd \
                           from raw_cs_cornerstone_DuplicateCourseError cs left join coursecatalog tc on lower(trim(cs.class_title)) = lower(trim(tc.coursename)) where cs.ValidInd=1").createOrReplaceTempView("raw_cs_cornerstone_DuplicatesError")

    #Combining duplicate records 
    finalInvalidDF = spark.sql("""select learner_id,class_title,class_id,date,last_name,first_name,learner_email,filename,filedate,ValidInd,ValidIndERR from
                                    raw_cs_cornerstone_completionLastName_person_email_valid_flag where ValidInd=0  
                                UNION 
                                select learner_id,class_title,class_id,date,last_name,first_name,learner_email,filename,filedate,ValidInd,ValidIndERR from 
                                raw_cs_cornerstone_DuplicatesError where ValidInd = 0
                                UNION 
                                select learner_id,class_title,class_id,date,last_name,first_name,learner_email,filename,filedate,ValidInd,ValidIndERR from 
                                raw_cs_cornerstone_DuplicateCourseError where ValidInd = 0 """)

    ## valid records process it to training history table
    spark.sql("select * from raw_cs_cornerstone_DuplicatesError where ValidInd=1" ).createOrReplaceTempView("raw_cc_course_completions")

    ## Combining coursecatalog  and completion details   
    cccompletionsdf = spark.sql("""select distinct sc.learner_id ,sc.class_title ,sc.date as completiondate ,tc.credithours,
                                tc.trainingprogramtype,tc.trainingprogramcode ,tc.courseid ,tc.coursetype ,tc.courselanguage ,tc.dshscourseid,
                                'NA' as instructorname, 'NA' as instructorid,'CORNERSTONE' as trainingsource,to_timestamp(sc.filedate) as filedate ,sc.filename 
                                from raw_cc_course_completions sc left join coursecatalog tc on lower(trim(sc.class_title)) = lower(trim(tc.coursename))""")

    print ("Valid records: {0}".format(cccompletionsdf.count()))

    ## creating DynamicFrame for valid indicator records to insert into training history table 
    traininghistorydf = DynamicFrame.fromDF(cccompletionsdf, glueContext, "traininghistorydf")

    # Script generated for node Apply Mapping
    ApplyMapping_node1646956720451 = ApplyMapping.apply(
        frame=traininghistorydf,
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
            ("filedate", "timestamp", "filedate", "timestamp"),
            ("dshscourseid", "string", "dshscourseid", "string"),
            ("filename", "string", "filename", "string"),
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
            "dshscourseid",
            "filename"
        ],
        transformation_ctx="selectFields_raw_trainghistory",
    )

    dyf_dropNullfields = DropNullFields.apply(frame = selectFields_raw_trainghistory)

    #Script generated for node PostgreSQL
    glueContext.write_dynamic_frame.from_catalog(
        frame=dyf_dropNullfields,
        database=catalog_database,
        table_name=catalog_table_prefix+"_raw_traininghistory"
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
                            .withColumnRenamed("status","Status")\
                            .withColumnRenamed("filename","Filename")\
                            .drop(col("ValidInd"))


        pandas_df = outboundDF.toPandas()

        suffix = outboundDF.first()["Filename"]
        pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/cornerstone/raw_to_raw_traininghistory_error_"+suffix, header = True, index = None, quotechar= '"', encoding ='utf-8', sep =',',quoting = csv.QUOTE_ALL)
        print(suffix)
        print ("Invalid records: {0}".format(finalInvalidDF.count()))

        # Adding to traininghistory logs
        finalInvalidDF.createOrReplaceTempView("finalInvalidDF")
        errordf = spark.sql("select cast(learner_id as long) personid, class_title as coursename, class_id as dshscourseid, cast(date as date) completeddate, 'NA' as instructorname, 'NA' as instructorid,'CORNERSTONE' as trainingsource,ValidIndERR as error_message,filename, filedate from finalInvalidDF")
        errorcdf = DynamicFrame.fromDF(errordf, glueContext, "historydf")

        glueContext.write_dynamic_frame.from_catalog(
        frame = errorcdf,
        database = catalog_database,
        table_name = catalog_table_prefix+"_logs_traininghistorylog",
        )

    print("Insert an entry into the log table")
    url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
    properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
    max_filedate = datetime.now()
    #max_filedate = raw_cs_cornerstone_completion_df.max()['filedate']
    logs_data = [[ max_filedate, "glue-cornerstone-completions-raw-to-raw-traininghistory", "1" ]] 		 
    logs_columns = ['lastprocesseddate', 'processname','success'] 		 
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
    mode = 'append'  		 
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
else:
    print("Data has already processed or no new data in the source table.")
    
print("****************Job execution completed*******************")
job.commit()