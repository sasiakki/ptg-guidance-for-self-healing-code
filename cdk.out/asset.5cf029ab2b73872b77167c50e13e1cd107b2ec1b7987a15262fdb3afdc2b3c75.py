#https://seiu775bg.atlassian.net/browse/DT-824
#Remove Smartsheet Course Completions from E2E Process

'''
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col,to_date,when,regexp_replace,lit,regexp_extract,input_file_name
import boto3
from pyspark.sql.types import StringType
import json
import re
from datetime import datetime,date
from heapq import nsmallest
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
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3'
    #SecretId='prod/b2bds/rds/system-pipelines'
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

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

print("************Starting glue job execution**********************")


files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/smartsheets/curated/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/smartsheets/curated/)(SmartSheet)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)", object_summary.key).group(3), '%Y%m%d%H%M%S').date()
        files_list[filename] = filedate

# Creating the md5 for comparision to the previous day's data and registering it to a Temp view 
sscompletionspreviousdf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_ss_course_completion", transformation_ctx = "sscompletionspreviousdf")

sscompletionspreviousdf.toDF().selectExpr("md5(concat_ws('',learner_id, first_name, last_name, phone_number, learner_email, attendance, class_id, class_title, date, duration,when_enrolled, instructor, sheet_name)) as sscompletionshashid").createOrReplaceTempView("sscompletionspreviousdf")

if len(files_list) !=0:
       
    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    
    # Script for S3 bucket to read file in format SmartSheet20220428045631.csv
    curated_smartsheetcompletions_cdf = glueContext.create_dynamic_frame.from_options(
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
        }
    ).toDF()

    curated_smartsheetcompletions_cdf.count()

    #Performing the data enrichment 
    curated_smartsheetcompletions_cdf = curated_smartsheetcompletions_cdf.withColumn("filename", input_file_name())
    curated_smartsheetcompletions_cdf = curated_smartsheetcompletions_cdf.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/Inbound/raw/smartsheets/curated/)(.*)', 4))
    curated_smartsheetcompletions_cdf = curated_smartsheetcompletions_cdf.withColumn("filedate",to_date(regexp_extract(col('filename'), 'SmartSheet(\\d{4}\\d{2}\\d{2}\\d{2}\\d{2}\\d{2})\\.csv', 1),"yyyyMMddHHmmss"))
    curated_smartsheetcompletions_cdf = curated_smartsheetcompletions_cdf.withColumn("date",to_date(col("date"),"MM/dd/yy")).withColumn("when enrolled",to_date(col("when enrolled"),"MM/dd/yy")).withColumn("duration",col("duration").cast("decimal(3,2)"))
    rawcompletions_unique = curated_smartsheetcompletions_cdf.dropDuplicates(['learner id', 'class id']).withColumn("date", when(col("date") == "" , None).otherwise(col("date")))
    rawcompletions_unique = rawcompletions_unique.filter(col("learner id").rlike("""^[0-9]+$""")).filter(col("date").isNotNull())
    rawcompletions_valid = rawcompletions_unique.withColumn("instructor",regexp_replace(col("instructor"), "[']", "’"))

    print("valid record count: {0} ".format(rawcompletions_unique.count()))
    
    #Extracting the invalid records 
    rawcompletions_invalid = curated_smartsheetcompletions_cdf.subtract(rawcompletions_valid)
    
    print("Invalid record count: {0} ".format(rawcompletions_invalid.count()))

    # Coverting  spark dataframe to glue dynamic dataframe
    rawcompletions_datasource = DynamicFrame.fromDF(rawcompletions_valid, glueContext, "rawcompletions_datasource")
    
    
    # ApplyMapping to match the target table
    rawcompletions_applymapping = ApplyMapping.apply(frame = rawcompletions_datasource, mappings = [("attendance", "string", "attendance", "string"), ("class id", "string", "class_id", "string"), ("class title", "string", "class_title", "string"), ("date", "date", "date", "date"), ("duration", "decimal(3,2)", "duration", "decimal(3,2)"), ("first name", "string", "first_name", "string"),("instructor", "string", "instructor", "string"), ("last name", "string", "last_name", "string"), ("learner email", "string", "learner_email", "string"), ("learner id", "string", "learner_id", "string"), ("phone number", "string", "phone_number", "string"), ("sheet name", "string", "sheet_name", "string"), ("when enrolled", "date", "when_enrolled", "date"),("filenamenew","string","filename","string"),("filedate","date","filedate","date")], transformation_ctx = "rawcompletions_applymapping")
    
     # Coverting glue dynamic dataframe to spark dataframe
    sscompletionsdf_clean = rawcompletions_applymapping.toDF()
    sscompletionsdf_clean.createOrReplaceTempView("sscompletionscleandf")
    
    # Creating the md5 for comparision 
    sscompletionsdf_clean = spark.sql(""" select *, md5(concat_ws('',learner_id, first_name, last_name, phone_number, learner_email, attendance, class_id, class_title, date, duration, when_enrolled, instructor, sheet_name)) as sscompletionshashid from sscompletionscleandf """)

    sscompletionsdf_clean.createOrReplaceTempView("sscompletionscleandf")

    # Capturing the delta if record is not previously processed with hash value
    sscompletionsdf_clean = spark.sql("""
      select *, true as isdelta from sscompletionscleandf where trim(sscompletionshashid) not in (select trim(sscompletionshashid) from sscompletionspreviousdf)
        UNION 
      select *, false as isdelta from sscompletionscleandf where trim(sscompletionshashid) in (select trim(sscompletionshashid) from sscompletionspreviousdf)
        """).drop("sscompletionshashid")

    # Truncating and loading the processed data
    sscompletionsdf_clean.write.option("truncate",True).jdbc(url=url, table="raw.ss_course_completion", mode=mode, properties=properties)
    #Saving Invalid records and exporting to S3 bucket
    if(rawcompletions_invalid.count() > 0):
        print("Exporting and Saving invalid records")
        rawcompletions_invalid = rawcompletions_invalid.withColumn("error_reason",when(col("learner id").isNull(),"PersonID is not Valid")
                                                                 .when(~col("learner id").rlike("""^[0-9]+$"""),"PersonID is not Valid")
                                                                 .when(col("date").isNull(),"Completion date is not valid")
                                                                 .when(to_date(col("date"),'MM/dd/yy').isNull(),"Completion date is not valid")
                                                                 .when(col("learner id") == "0","PersonID is not Valid")
                                                                 .otherwise("Duplicate record"))
                                                                 

        #name_suffix = rawcompletions_invalid.select("filenamenew").distinct().limit(1).collect()
        #name_suffix = name_suffix[0].filenamenew
        today = date.today()
        suffix = today.strftime("%Y-%m-%d")
        #print(name_suffix)
        #rawcompletions_invalid = rawcompletions_invalid.drop("filename")
        #rawcompletions_invalid = rawcompletions_invalid.withColumnRenamed("filenamenew","filename")
        rawcompletions_invalid.printSchema()
        #rawcornerstonecompletions_invalid.show(2,vertical=True)
        pandas_df = rawcompletions_invalid.toPandas()
        print("Exporting to S3 bucket")
    
        # Export the invalid records to a S3 bucket
        pandas_df.to_csv("s3://"+ S3_BUCKET + "/Outbound/smartsheet_course_completion/Smartsheet_errors_s3_to_raw-" + suffix+".csv", header=True, index=None, sep=',')
    
        #Insert the invalid records in to logs.smartsheeterros table
        ##Get invalid rows and insert to logs table
        newdatasource1 = DynamicFrame.fromDF(rawcompletions_invalid, glueContext, "newdatasource1")
        # ApplyMapping to match the target table
        rawcompletions_invalid_applymapping = ApplyMapping.apply(frame = newdatasource1, mappings =  [("attendance", "string", "attendance", "string"), ("class id", "string", "class_id", "string"), ("class title", "string", "class_title", "string"), ("date", "date", "date", "date"), ("duration", "decimal(3,2)", "duration", "decimal(3,2)"), ("first name", "string", "first_name", "string"),("instructor", "string", "instructor", "string"), ("last name", "string", "last_name", "string"), ("learner email", "string", "learner_email", "string"), ("learner id", "string", "learner_id", "string"), ("phone number", "string", "phone_number", "string"), ("sheet name", "string", "sheet_name", "string"), ("when enrolled", "date", "when_enrolled", "date"),("error_reason","string","error_reason","string"),("filenamenew","string","filename","string"),("filedate","date","filedate","date")], transformation_ctx = "rawcompletions_invalid_applymapping")
    
        # Coverting glue dynamic dataframe to spark dataframe
        sscompletionsdf_invalid = rawcompletions_invalid_applymapping.toDF()
        sscompletionsdf_invalid.show(50)
        mode = 'append'
        sscompletionsdf_invalid.write.jdbc(url=url, table="logs.smartsheeterrors", mode=mode, properties=properties) 
        

    
    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    #copy_source = {  'Bucket': 'seiubg-b2bds-prod-feeds-fp7mk','Key': sourcekey }prod 
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
print("************Completed glue job execution**********************")
job.commit()

'''