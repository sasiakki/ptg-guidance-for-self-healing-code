
#Remove Qualtrics DSHS O&S Feed from E2E Process
#https://seiu775bg.atlassian.net/browse/DT-551

'''
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.sql.functions import col,when,input_file_name,regexp_extract,to_timestamp
import boto3
import json
import re
from datetime import datetime
from heapq import nsmallest

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

args_JSON = getResolvedOptions(sys.argv, ["account_number"])
aws_account = args_JSON['account_number']

if aws_account == '259367569391' :
    environment_type = 'prod'
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'
else:
    environment_type = 'dev'
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'


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

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}


# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/qualtrics/DSHS_O&S_Completed/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/qualtrics/DSHS_O&S_Completed/)(DSHS_O&S_Completed)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)", object_summary.key).group(3), '%Y%m%d%H%M%S').date()
        files_list[filename] = filedate

if len(files_list) !=0:
    
    # For Qualtrics DSHS O&S Completions, we always load the full file data for every run, capturing the responseid of the pervious run to differentiate the old and new records . 
    # isDelta flag  is marked as true for new responseid not existing in data store and false for otherwise 
    dshspersonospreviousdf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_dshs_os_qual_agency_person", transformation_ctx = "dshspersonospreviousdf")
    dshspersonospreviousdf.toDF().select("responseid").createOrReplaceTempView("dshspersonospreviousdf")
    
    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    # Script generated for node S3 bucket
    dshspersonosdf = glueContext.create_dynamic_frame.from_options(
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
        transformation_ctx="dshspersonosdf",
    )
    # Capturing the processing file name, date and marking empty columns as null's 
    dshspersonosdf = dshspersonosdf.toDF().withColumn("filename", input_file_name())
    dshspersonosdf = dshspersonosdf.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/Inbound/raw/qualtrics/DSHS_O&S_Completed/)(.*)', 4))
    dshspersonosdf = dshspersonosdf.withColumn("filemodifieddate",to_timestamp(regexp_extract(col('filenamenew'), '(DSHS_O&S_Completed)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)', 2),"yyyyMMddHHmmss"))
    dshspersonosdf = dshspersonosdf.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in dshspersonosdf.columns])

    dshspersonosdf = DynamicFrame.fromDF(dshspersonosdf, glueContext, "dyf")


    # Mapping of the filename columns to the target table coumns with its datatypes
    dshspersonosdf = ApplyMapping.apply(
        frame=dshspersonosdf,
        mappings=[
            ("startdate", "string", "startdate", "string"),
            ("filenamenew","string","filename","string"),
            ("filemodifieddate","timestamp","filemodifieddate","timestamp"),
            ("enddate", "string", "enddate", "string"),
            ("status", "string", "status", "string"),
            ("ipaddress", "string", "ipaddress", "string"),
            ("progress", "string", "progress", "string"),
            ("duration (in seconds)", "string", "duration_in_seconds", "string"),
            ("finished", "string", "finished", "string"),
            ("recordeddate", "string", "recordeddate", "string"),
            ("responseid", "string", "responseid", "string"),
            ("recipientlastname", "string", "recipientlastname", "string"),
            ("recipientfirstname", "string", "recipientfirstname", "string"),
            ("recipientemail", "string", "recipientemail", "string"),
            ("externalreference", "string", "externalreference", "string"),
            ("locationlatitude", "string", "locationlatitude", "string"),
            ("locationlongitude", "string", "locationlongitude", "string"),
            ("distributionchannel", "string", "distributionchannel", "string"),
            ("userlanguage", "string", "userlanguage", "string"),
            ("q_recaptchascore", "string", "q_recaptchascore", "string"),
            ("q2_1", "string", "agency_firstname", "string"),
            ("q2_2", "string", "agency_lastname", "string"),
            ("q2_3", "string", "agency_email", "string"),
            ("q4", "string", "employername", "string"),
            ("q5_1", "string", "person_firstname", "string"),
            ("q5_2", "string", "person_lastname", "string"),
            ("q5_3", "string", "person_dob", "string"),
            ("q5_4", "string", "person_phone", "string"),
            ("q5_5", "string", "dshs_id", "string"),
            ("q13", "string", "os_completion_date", "string"),
        ],
        transformation_ctx="dshspersonosdf",
    )

    # Script generated for node PostgreSQL table
    dshspersonosdf.toDF().createOrReplaceTempView("dshspersonoscleandf")

    spark.sql("select trim(responseid) from dshspersonospreviousdf").show()
    spark.sql("select *, true as isdelta from dshspersonoscleandf where trim(responseid) not in (select trim(responseid) from dshspersonospreviousdf)").show()
    spark.sql("select *, false as isdelta from dshspersonoscleandf where trim(responseid) in (select trim(responseid) from dshspersonospreviousdf)").show()

    # isDelta flag  is marked as true for new responseid not existing in data store and false for otherwise 
    dshspersonosdf_clean = spark.sql("""
    select *, true as isdelta from dshspersonoscleandf where trim(responseid) not in (select trim(responseid) from dshspersonospreviousdf)
        UNION 
    select *, false as isdelta from dshspersonoscleandf where trim(responseid) in (select trim(responseid) from dshspersonospreviousdf)
        """)

    dshspersonosdf_clean.write.option("truncate",True).jdbc(url=url, table="raw.dshs_os_qual_agency_person", mode=mode, properties=properties)

    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()

job.commit()
'''