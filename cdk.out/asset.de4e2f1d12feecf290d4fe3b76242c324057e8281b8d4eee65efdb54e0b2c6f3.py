import sys
from awsglue.transforms import *
from pyspark.context import SparkContext
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col,when,input_file_name,regexp_extract,to_timestamp
from pyspark.sql.functions import *
from pyspark.sql.types import LongType,DateType
import boto3
import json
import re
from datetime import datetime
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


# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['fileexchange']

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
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

mode = "append"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,
              "driver": "org.postgresql.Driver"}

# Multiple files of the completions can be processed in same time
sourcepath = "s3://"+S3_BUCKET+"/transcripts/corrections/forprocessing/"


datasource1 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource1")
logslastprocessed = datasource1.toDF().createOrReplaceTempView("vwlogslastprocessed")

print("************Starting glue job execution**********************")

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="transcripts/corrections/forprocessing/"):
      if object_summary.key.endswith('csv'):
          path = object_summary.key
          filename = object_summary.key
          filedate = datetime.strptime(re.search(r"(transcripts/corrections/forprocessing/)(TranscriptCorrections_)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)", object_summary.key).group(3), '%Y%m%d%H%M%S').date()
          print(filedate)
          files_list[filename] = filedate



if len(files_list) !=0:
    rawcorrections = spark.read.format("csv").option("header","true").option("inferSchema","false").option("escape","\"").load(f"{sourcepath}")
    spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
    rawcorrections = rawcorrections.withColumn("filename", input_file_name())
    rawcorrections = rawcorrections.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/transcripts/corrections/forprocessing/)(.*)', 4))
    filename = rawcorrections.select("filenamenew").distinct().limit(1).collect()
    filename = filename[0].filenamenew
    print(filename)
    rawcorrections = rawcorrections.withColumn("filedate",to_timestamp(regexp_extract(col('filename'), '(TranscriptCorrections_)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)', 2),"yyyyMMddHHmmss"))
    max_filedate = rawcorrections.first()["filedate"]
    print(max_filedate)
    rawcorrections = rawcorrections.withColumn("completed", to_date(col("completed"), "yyyy-mm-dd").cast(DateType()))
    rawcorrections.createOrReplaceTempView("vwrawcorrections")
    #Insert into raw table only if new file filedate > lastprocesseddate
    rawcorrections = spark.sql(f"""SELECT * FROM vwrawcorrections WHERE filedate >
                                                (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                                END AS MAXPROCESSDATE FROM vwlogslastprocessed
                                                WHERE processname='glue-transcript-corrections-s3-to-raw' AND success='1')""")

    if(rawcorrections.count() > 0):
        print("New file is processing")
        print("Total record count: {0} ".format(rawcorrections.count()))

        # Check if the personid is has only digits and completion date is not null
        rawcorrections_valid = rawcorrections.filter(col("PERSONID").isNotNull()).filter(col("PERSONID").rlike("""^[0-9]+$""")).filter(col("COMPLETED").isNotNull()).filter(col("COURSEID").isNotNull())
        rawcorrections_valid.show(2)
        print("Valid record count: {0} ".format(rawcorrections_valid.count()))

        #Extracting the invalid records
        rawcorrections_invalid = rawcorrections.subtract(rawcorrections_valid)
        rawcorrections_invalid.show(2)
        print("Invalid record count: {0} ".format(rawcorrections_invalid.count()))

        #Converting the spark to glue df
        rawcorrections_catalog = DynamicFrame.fromDF(rawcorrections_valid, glueContext, "rawcorrections_catalog")
        #Apply Mapping to match the target table and datatype
        rawcorrections_targetmapping = ApplyMapping.apply(
            frame=rawcorrections_catalog,
            mappings=[
            ("PERSONID", "string", "personid", "long"),
            ("COURSEID", "string", "courseid", "string"),
            ("DSHSCOURSEID", "string", "dshscourseid", "string"),
            ("CREDITS", "string", "credithours", "float"),
            ("COMPLETED", "date", "completeddate", "date"),
            ("COURSENAME", "string", "coursename", "string"),
            ("INSTRUCTORID", "string", "INSTRUCTORID", "string"),
            ("INSTRUCTOR", "string", "INSTRUCTOR", "string"),
            ("TRAININGSOURCE", "string", "trainingsource", "string"),
            ("filenamenew","string","filename","string"),
            ("filedate", "timestamp", "filedate", "timestamp")
            ],
            transformation_ctx="rawcorrections_targetmapping",
        )

        # Coverting glue dynamic dataframe to spark dataframe
        rawcorrectionsfinaldf = rawcorrections_targetmapping.toDF()
        rawcorrectionsfinaldf.show(2)

        # Truncating and loading the processed data
        rawcorrectionsfinaldf.write.jdbc(url=url, table="raw.transcriptcorrections", mode=mode, properties=properties)
        #Saving Invalid records and exporting to S3 bucket
        if(rawcorrections_invalid.count() > 0):
            print("Exporting and Saving invalid records")
            rawcorrections_invalid = rawcorrections_invalid.withColumn("errorreason",when(col("PERSONID").isNull() & col("COMPLETED").isNull() & col("COURSEID").isNull(),"Person ID and Course ID and Completion date is not valid").when(~col("PERSONID").rlike("^\d+$") | col("PERSONID").isNull(),"Person ID is not valid").when(col("COMPLETED").isNull(),"Completion date is not valid").when(col("COURSEID").isNull(),"Course ID is not valid"))
            name_suffix = rawcorrections_invalid.select("filenamenew").distinct().limit(1).collect()
            name_suffix = name_suffix[0].filenamenew
            print(name_suffix)
            rawcorrections_invalid = rawcorrections_invalid.drop("filename")
            rawcorrections_invalid = rawcorrections_invalid.withColumnRenamed("filenamenew","filename")
            pandas_df = rawcorrections_invalid.toPandas()
            print("Exporting to S3 bucket")
            # Export the invalid records to a S3 bucket
            pandas_df.to_csv("s3://"+ S3_BUCKET + "/transcripts/corrections/errors/s3_to_raw_error_" + name_suffix, header=True, index=None,quotechar='"',encoding='utf-8', sep=',',quoting=csv.QUOTE_ALL)

        #Insert the invalid records in to logs.transcriptcorrectionerrors table
        ##Get invalid rows and insert to logs table
        newdatasource1 = DynamicFrame.fromDF(rawcorrections_invalid, glueContext, "newdatasource1")
        applymapping1 = ApplyMapping.apply(frame = newdatasource1, mappings = [
            ("PERSONID", "string", "personid", "string"),
            ("COURSEID", "string", "courseid", "string"),
            ("DSHSCOURSEID", "string", "dshscourseid", "string"),
            ("CREDITS", "string", "credithours", "float"),
            ("COMPLETED", "date", "completeddate", "date"),
            ("COURSENAME", "string", "coursename", "string"),
            ("INSTRUCTORID", "string", "INSTRUCTORID", "string"),
            ("INSTRUCTOR", "string", "INSTRUCTOR", "string"),
            ("TRAININGSOURCE", "string", "trainingsource", "string"),
            ("filename","string","filename","string"),
            ("filedate", "timestamp", "filedate", "timestamp"),
            ("errorreason","string","errorreason","string")],
            transformation_ctx = "applymapping1")
        new_df1 = applymapping1.toDF()
        print("Inserting invalid records into logs table")
        mode = "append"
        new_df1.write.jdbc(url=url, table="logs.transcriptcorrectionerrors", mode=mode, properties=properties)

        print("Insert an entry into the log table")
        #max_filedate = rawcorrectionsfinaldf.first()["filedate"]
        max_filedate = rawcorrections.orderBy(desc("filedate")).limit(1).first()["filedate"]
        logs_data = [[max_filedate, "glue-transcript-corrections-s3-to-raw", "1"]]
        logs_columns = ['lastprocesseddate', 'processname','success']
        logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
        logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)

    else:
        print("File has already processed or no records in the file.")

    print("Archiving the File.")
    #Archiving Processed files
    #If we have Multiple files of the completions, then one file at time is moved to archive location
    
    for object_summary in s3bucket.objects.filter(Prefix="transcripts/corrections/forprocessing"):
        if object_summary.key.endswith('csv') and "error" not in object_summary.key and "processed" not in object_summary.key:
            filename = object_summary.key
            sourcekey = filename
            targetkey =  sourcekey.replace("/corrections/forprocessing/","/corrections/processed/")
            copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
            s3bucket.copy(copy_source, targetkey)
            s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
else:
    print("No new file in S3 Bucket for processing!!!!")

job.commit()
