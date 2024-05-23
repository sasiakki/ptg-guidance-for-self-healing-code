import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col,to_date,when,regexp_replace,lit,regexp_extract,input_file_name,current_date,date_format,to_timestamp
from pyspark.sql.types import StringType
from pyspark.sql.functions import *
import boto3
import json
import re
from datetime import datetime,date
from heapq import nsmallest
from heapq import nlargest
import pandas as pd
import csv

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Setting the timeParserPolicy as legacy for handling multiple types of date formats received in docebo_ILT_course_completion responses  
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
    
#Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

#Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3'
)

s3response_docebo = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3_docebo'
)

s3_secrets_docebo = json.loads(s3response_docebo['SecretString'])
S3_BUCKET_docebo = s3_secrets_docebo['datafeeds']

s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']

#Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId = environment_type+'/b2bds/rds/system-pipelines'
)

database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

# Reading files from s3 
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

#Everday the doceboILTCompletions file is uploaded to seiu-learning-center bucket. During file processing, we copy the file from source bucket to Inbound/raw/doceboilt/doceboILTCompletions.csv
copy_source= {
    'Bucket': S3_BUCKET_docebo,
    'Key': 'doceboILT/doceboILTCompletions.csv'
}

#Copy the file from the source bucket to the destination bucket
s3bucket.copy(copy_source, 'Inbound/raw/doceboilt/doceboILTCompletions.csv')

# Multiple files of the completions can be processed in same time
sourcepath = "s3://"+S3_BUCKET+"/Inbound/raw/doceboilt/"
    
#Creating the md5 for comparision to the previous day's data and registering it to a Temp view 
doceboiltpreviousdf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_doceboilt_course_completion", transformation_ctx = "doceboiltpreviousdf")

doceboiltpreviousdf.toDF().selectExpr("md5(concat_ws('',username,firstname,lastname,trainingid,coursename,coursecode,credits,dshscode,sessioninstructor,sessionname,eventinstructor,completiondate)) as doceboilthashid ").createOrReplaceTempView("doceboiltpreviousdf_hash")

print("previous day records count")
spark.sql("""select count(*) from doceboiltpreviousdf_hash""").show()

# Script for S3 bucket to read file in format doceboiltCourseCompletions.csv
doceboilt_coursecompletion = spark.read.format("csv").option("header","true").option("inferSchema","false").option("escape","\"").load(f"{sourcepath}")
#There is no timestamp in the filename received from source, we are using current_date as filedate
doceboilt_coursecompletion = doceboilt_coursecompletion.withColumn("filename", input_file_name())
doceboilt_coursecompletion = doceboilt_coursecompletion.withColumn("filename",regexp_extract(col('filename'), '(s3://)(.*)(/Inbound/raw/doceboilt/)(.*)', 4)) \
                                                       .withColumn("filedate", current_date()) \
                                                       .withColumn("Session instructor full name",regexp_replace(col("Session instructor full name"), "[']", "’")) \
                                                       .withColumn("Completion Date", to_date("Completion Date", "yyyy-MM-dd HH:mm").cast('string'))
                                                       
#Extracting the valid records
doceboilt_coursecompletion_valid = doceboilt_coursecompletion.filter(col("Username").rlike("""^[0-9]+$""")).filter(col("Completion Date").isNotNull()).filter(col("Username").isNotNull()).filter(col("Completion Date") >= '2023-03-20')
    
#Extracting the invalid records 
doceboilt_coursecompletion_invalid = doceboilt_coursecompletion.subtract(doceboilt_coursecompletion_valid)

#Converting the spark to glue df 
doceboilt_coursecompletion_catalog = DynamicFrame.fromDF(doceboilt_coursecompletion_valid, glueContext, "doceboilt_coursecompletion_catalog")
    #Apply Mapping to match the target table and datatype 
doceboilt_coursecompletion_targetmapping = ApplyMapping.apply(
            frame=doceboilt_coursecompletion_catalog,
            mappings=[
                ("Username", "string", "username", "string"),
                ("First Name", "string", "firstname", "string"),
                ("Last Name", "string", "lastname", "string"),
                ("TrainingID", "string", "trainingid", "string"),
                ("Course Name", "string", "coursename", "string"),
                ("Course code", "string", "coursecode", "string"),
                ("Credits (CEUs)", "string", "credits", "string"),
                ("DSHS Code", "string", "dshscode", "string"),
                ("Session instructor full name", "string", "sessioninstructor", "string"),
                ("Session Name", "string", "sessionname", "string"),
                ("Event Instructor Full Name", "string", "eventinstructor", "string"),
                ("Completion Date", "string", "completiondate", "string"),
                ("filename", "string", "filename", "string"),
                ("filedate", "date", "filedate", "date")
            ],
            transformation_ctx="doceboilt_coursecompletion_targetmapping",
        )
    
# Coverting glue dynamic dataframe to spark dataframe
doceboilt_coursecompletionfinaldf = doceboilt_coursecompletion_targetmapping.toDF()

doceboilt_coursecompletionfinaldf.createOrReplaceTempView("doceboiltcleandf")
    
# Creating the md5 for comparision 
doceboilt_clean = spark.sql(""" select *, md5(concat_ws('',username,firstname,lastname,trainingid,coursename,coursecode,credits,dshscode,sessioninstructor,sessionname,eventinstructor,completiondate)) as doceboilthashid from doceboiltcleandf """)
    
doceboilt_clean.createOrReplaceTempView("doceboiltcleandf")
    
# Capturing the delta if record is not previously processed with hash value
doceboilt_clean = spark.sql("""
          select *, true as isdelta from doceboiltcleandf where trim(doceboilthashid) not in (select trim(doceboilthashid) from doceboiltpreviousdf_hash)
            UNION 
          select *, false as isdelta from doceboiltcleandf where trim(doceboilthashid) in (select trim(doceboilthashid) from doceboiltpreviousdf_hash)
            """).drop("doceboilthashid")
            
#Truncating and loading the processed data
doceboilt_clean.write.option("truncate",True).jdbc(url=url, table="raw.doceboilt_course_completion", mode=mode, properties=properties)

#Saving Invalid records and exporting to S3 bucket
if(doceboilt_coursecompletion_invalid.count() > 0):
    print("Exporting and Saving invalid records")
    #processing for invalid records
    doceboilt_coursecompletion_invalid=doceboilt_coursecompletion_invalid.withColumn("error_reason",
                                                                      when(col("Username").isNull(),"PersonID is not Valid")
                                                                     .when(~col("Username").rlike("""^[0-9]+$"""),"PersonID is not Valid")
                                                                     .when(col("Completion Date").isNull(),"Completion date is not valid")
                                                                     .when(col("Username") == "0","PersonID is not Valid")
                                                                     .when(col("Completion Date") < '2023-03-20',"Completion Date is before 2023-03-20"))
    #Converting the spark to glue df 
    doceboilt_coursecompletioninvalid_catalog = DynamicFrame.fromDF(doceboilt_coursecompletion_invalid, glueContext, "doceboilt_coursecompletioninvalid_catalog")
        #Apply Mapping to match the target table and datatype 
    doceboilt_coursecompletion_invalid_targetmapping = ApplyMapping.apply(
                frame=doceboilt_coursecompletioninvalid_catalog,
                mappings=[
                    ("Username", "string", "username", "string"),
                    ("First Name", "string", "firstname", "string"),
                    ("Last Name", "string", "lastname", "string"),
                    ("TrainingID", "string", "trainingid", "string"),
                    ("Course Name", "string", "coursename", "string"),
                    ("Course code", "string", "coursecode", "string"),
                    ("Credits (CEUs)", "string", "credits", "string"),
                    ("DSHS Code", "string", "dshscode", "string"),
                    ("Session instructor full name", "string", "sessioninstructor", "string"),
                    ("Session Name", "string", "sessionname", "string"),
                    ("Event Instructor Full Name", "string", "eventinstructor", "string"),
                    ("Completion Date", "string", "completiondate", "string"),
                    ("filename", "string", "filename", "string"),
                    ("filedate", "date", "filedate", "date"),
                    ("error_reason", "string", "error_reason", "string")
                ],
                transformation_ctx="doceboilt_coursecompletion_invalid_targetmapping",
            )
        
    #Coverting glue dynamic dataframe to spark dataframe
    doceboilt_coursecompletionfinalinvaliddf = doceboilt_coursecompletion_invalid_targetmapping.toDF()
    
    #appending invalid logs to doceboilterrors
    mode = 'append'
    doceboilt_coursecompletionfinalinvaliddf.write.jdbc(url=url, table="logs.doceboilterrors", mode=mode, properties=properties)
    
    today = date.today()
    suffix = today.strftime("%Y-%m-%d")
            
    pandas_df = doceboilt_coursecompletion_invalid.toPandas()
        
    #Export the invalid records to a S3 bucket
    pandas_df.to_csv("s3://"+ S3_BUCKET + "/Outbound/doceboilt/DoceboILT_s3_to_raw_errors_" + suffix+".csv", header=True, index=None, sep=',')

if(doceboilt_clean.count() > 0 or  doceboilt_coursecompletion_invalid.count() > 0):
    print("Insert an entry into the log table")
    max_filedate = datetime.now()
    logs_data = [[max_filedate, "glue-docebo-ilt-coursecompletions-s3-to-raw", "1"]]
    logs_columns = ['lastprocesseddate', 'processname','success']
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
    mode = 'append'
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)

file_date = datetime.now().strftime("%Y%m%d%H%M%S")
#Moving the processed file to archive location
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/doceboilt/"):
   if object_summary.key.endswith('csv'):
     filename = object_summary.key
     sourcekey = filename 
     targetkey = sourcekey.replace("/raw/", "/archive/").replace(".csv","_"+file_date+".csv")
     copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
     s3bucket.copy(copy_source, targetkey)
     s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
job.commit()