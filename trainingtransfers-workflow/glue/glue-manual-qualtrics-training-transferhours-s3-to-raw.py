import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import StringType,TimestampType
from pyspark.sql.functions import when,col,input_file_name,to_date,regexp_extract
import boto3
import json
import re
from datetime import datetime
from heapq import nsmallest

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

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')
# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']
# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId = environment_type+'/b2bds/rds/system-pipelines'
)
database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']
mode = "append"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')
files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/manualtransferhours/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/manualtransferhours/)(Transfer hours )(\d\d\d\d-\d\d-\d\d)(.csv)", object_summary.key).group(3), '%Y-%m-%d').date()
        files_list[filename] = filedate
print(files_list)        

if len(files_list) !=0:

    ## B2BDS-1385: loglast DF
    logslastprocesseddf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "logsdf")
    logslastprocesseddf = logslastprocesseddf.toDF().createOrReplaceTempView("logslastprocessed")

    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    # Script for S3 bucket to read file in format Transfer hours 2022-04-28.csv
    curated_transferedhourscompletions_cdf = glueContext.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": '"',
            "withHeader": True,
            "separator": ",",
            "optimizePerformance": True,
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [sourcepath],
            "recurse": True,
        },
        transformation_ctx="curated_transferedhourscompletions_cdf",
    )
    # Capturing the processing file name, date and marking empty columns as null's 
    curated_transferedhourscompletions_cdf = curated_transferedhourscompletions_cdf.toDF().withColumn("inputfilename", input_file_name())
    curated_transferedhourscompletions_cdf = curated_transferedhourscompletions_cdf.withColumn("filename",regexp_extract(col('inputfilename'), '(s3://)(.*)(/Inbound/raw/manualtransferhours/)(.*)', 4))
    curated_transferedhourscompletions_cdf = curated_transferedhourscompletions_cdf.withColumn("filedate",to_date(regexp_extract(col('filename'), 
    '(Transfer hours )(\d\d\d\d-\d\d-\d\d)(.csv)', 2),"yyyy-MM-dd"))
    curated_transferedhourscompletions_cdf = curated_transferedhourscompletions_cdf.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in curated_transferedhourscompletions_cdf.columns]).filter(curated_transferedhourscompletions_cdf.PersonID != '')
	
    curated_transferedhourscompletions_cdf =curated_transferedhourscompletions_cdf.withColumn('reason_code',col('reason_code\r'))
    curated_transferedhourscompletions_cdf = curated_transferedhourscompletions_cdf.withColumn("Completed",col("Completed").cast(TimestampType()))  
    
    ## B2BDS-1385: Insert into raw table only if new file filemodifieddate > lastprocesseddate
    curated_transferedhourscompletions_cdf = curated_transferedhourscompletions_cdf.createOrReplaceTempView("transferhoursdata")
    curated_transferedhourscompletions_cdf = spark.sql("""SELECT * FROM transferhoursdata WHERE filedate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                  END AS MAXPROCESSDATE FROM logslastprocessed  WHERE processname='glue-manual-qualtrics-training-transferhours-s3-to-raw' AND success='1')""")

    # Coverting  spark dataframe to glue dynamic dataframe
    rawcompletions_datasource = DynamicFrame.fromDF(curated_transferedhourscompletions_cdf, glueContext, "rawcompletions_datasource")
    # ApplyMapping to match the target table
    rawcompletions_applymapping = ApplyMapping.apply(frame = rawcompletions_datasource, mappings = [("PersonID", "string", "personid", "string"), ("CourseID", "string", "CourseID", "string"), ("DSHSID", "string", "DSHSID", "string"), ("Credits", "string", "Credits", "string"),("Completed", "timestamp", "Completed", "timestamp"), ("CourseName", "string", "CourseName", "string"), 
        ("Instructor", "string", "Instructor", "string"), ("Instructorid", "string", "Instructorid", "string"), 
        ("source", "string", "source", "string"), ("reason_code", "string", "reason_code", "string"),("filename", "string", "filename", "string"),("filedate", "date", "filedate", "date"),], transformation_ctx = "rawcompletions_applymapping")
    # Coverting glue dynamic dataframe to spark dataframe
    qulatricsagencytransfersdf_clean = rawcompletions_applymapping.toDF()

    # Truncating and loading the processed data
    qulatricsagencytransfersdf_clean.write.jdbc(url=url, table="raw.qualtrics_transfer_hours", mode=mode, properties=properties)
    
    ## B2BDS-1385: insert an entry into the log
    # Write a record with process/execution time to logs.lastprocessed table
    lastprocessed_df = spark.createDataFrame(
        [('glue-manual-qualtrics-training-transferhours-s3-to-raw', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])

    # Create Dynamic Frame to log lastprocessed table
    lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext,"lastprocessed_cdf")
    lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[("processname", "string", "processname", "string"), (
        "lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"), ("success", "string", "success", "string")])

    # Write to postgresql logs.lastprocessed table of the success
    glueContext.write_dynamic_frame.from_catalog(
        frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")

    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
## B2BDS-1385: the else clause in case the files_list is empty
else:
    print("No file found in S3")

job.commit()