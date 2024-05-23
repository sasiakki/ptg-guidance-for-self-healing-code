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
from pyspark.sql.types import LongType
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
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"

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
sourcepath = "s3://"+S3_BUCKET+"/Inbound/raw/docebo/"

datasource1 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource1")
logslastprocessed = datasource1.toDF().createOrReplaceTempView("vwlogslastprocessed")

print("************Starting glue job execution**********************")

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/docebo/"):
      if object_summary.key.endswith('csv'):
          path = object_summary.key
          filename = object_summary.key
          filedate = datetime.strptime(re.search(r"(Inbound/raw/docebo/)(Docebocoursecompletions_)(\d\d\d\d_\d\d_\d\d_\d\d_\d\d)(.csv)", object_summary.key).group(3), '%Y_%m_%d_%H_%M').date()
          files_list[filename] = filedate
          

if len(files_list) !=0:
    docebo_coursecompletion = spark.read.format("csv").option("header","true").option("inferSchema","false").option("escape","\"").load(f"{sourcepath}")
    spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
    #Capturing the processing file name, date and marking empty columns as null's Docebocoursecompletions_YYYY_MM_DD_hh_mm
    docebo_coursecompletion = docebo_coursecompletion.withColumn("filename", input_file_name())
    docebo_coursecompletion = docebo_coursecompletion.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/Inbound/raw/docebo/)(.*)', 4))
    docebo_coursecompletion = docebo_coursecompletion.withColumn("filedate",to_timestamp(regexp_extract(col('filename'), '(Docebocoursecompletions_)(\d\d\d\d_\d\d_\d\d_\d\d_\d\d)(.csv)', 2),"yyyy_MM_dd_HH_mm"))
    processingfilename = docebo_coursecompletion.first()["filenamenew"]
    print(processingfilename)
    print(filedate)
    docebo_coursecompletion.createOrReplaceTempView("vwdocebo_coursecompletion")
    #Insert into raw table only if new file filedate > lastprocesseddate
    docebo_coursecompletion = spark.sql("""SELECT * FROM vwdocebo_coursecompletion WHERE filedate >
                                                (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                                END AS MAXPROCESSDATE FROM vwlogslastprocessed 
                                                WHERE processname='glue-docebo-coursecompletions-s3-to-raw' AND success='1')""")

    if(docebo_coursecompletion.count() > 0):
        print("New file is processing")
        print("Total record count: {0} ".format(docebo_coursecompletion.count()))
        # marking empty columns as null's
        docebo_coursecompletion = docebo_coursecompletion.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in docebo_coursecompletion.columns])
    
        # Check if the personid is has only digits, if not making them as null
        docebo_coursecompletion_valid = docebo_coursecompletion.filter(col("Username").rlike("""^[0-9]+$""")).filter(col("Completion Date").isNotNull()).filter(col("Course Name").isNotNull()).filter(col("Course code").isNotNull())
        #docebo_coursecompletion_valid.show(2)
        print("Valid record count: {0} ".format(docebo_coursecompletion_valid.count()))
    
        #Extracting the invalid records 
        docebo_coursecompletion_invalid = docebo_coursecompletion.subtract(docebo_coursecompletion_valid)
        #docebo_coursecompletion_invalid.show(2)
        print("Invalid record count: {0} ".format(docebo_coursecompletion_invalid.count()))

        #Converting the spark to glue df 
        docebo_coursecompletion_catalog = DynamicFrame.fromDF(docebo_coursecompletion_valid, glueContext, "docebo_coursecompletion_catalog")
        #Apply Mapping to match the target table and datatype 
        docebo_coursecompletion_targetmapping = ApplyMapping.apply(
            frame=docebo_coursecompletion_catalog,
            mappings=[
            ("Username", "string", "username", "bigint"),
            ("First name", "string", "firstname", "string"),
            ("Last name", "string", "lastname", "string"),
            ("Course code", "string", "coursecode", "string"),
            ("Course Type", "string", "coursetype", "string"),
            ("Course Name", "string", "coursename", "string"),
            ("First access date", "string", "firstaccessdate", "string"),
            ("Completion Date", "string", "completiondate", "string"),
            ("Status", "string", "status", "string"),
            ("Credits (CEUs)", "string", "credithours", "string"),
            ("DSHS ID", "string", "dshsid", "string"),
            ("CDWA ID", "string", "cdwaid", "string"),
            ("TrainingID", "string", "trainingid", "string"),
            ("DSHS Code", "string", "dshscode", "string"),
            ("filenamenew", "string", "filename", "string"),
            ("filedate", "timestamp", "filedate", "timestamp")
            ],
            transformation_ctx="docebo_coursecompletion_targetmapping",
        )

        # Coverting glue dynamic dataframe to spark dataframe
        docebo_coursecompletionfinaldf = docebo_coursecompletion_targetmapping.toDF()
        #docebo_coursecompletionfinaldf.show(2)

        # Truncating and loading the processed data
        docebo_coursecompletionfinaldf.write.jdbc(url=url, table="raw.docebo_course_completion", mode=mode, properties=properties)
        #Saving Invalid records and exporting to S3 bucket
        if(docebo_coursecompletion_invalid.count() > 0):
            print("Exporting and Saving invalid records")
            docebo_coursecompletion_invalid = docebo_coursecompletion_invalid.withColumn("error_reason",when(col("Username").isNull(),"PersonID is not Valid")
                                                                 .when(col("Completion Date").isNull(),"Completion date is not valid")
                                                                 .when(col("Course code").isNull(),"CourseID is not valid")
                                                                 .when(col("Username") == "0","PersonID is not Valid")
                                                                 .when(col("Username").isNotNull(),"PersonID is not Valid"))
        
            name_suffix = docebo_coursecompletion_invalid.select("filenamenew").distinct().limit(1).collect()
            name_suffix = name_suffix[0].filenamenew
            print(name_suffix)
            docebo_coursecompletion_invalid = docebo_coursecompletion_invalid.drop("filename")
            docebo_coursecompletion_invalid = docebo_coursecompletion_invalid.withColumnRenamed("filenamenew","filename")
            pandas_df = docebo_coursecompletion_invalid.toPandas()
            print("Exporting to S3 bucket")
            # Export the invalid records to a S3 bucket
            pandas_df.to_csv("s3://"+ S3_BUCKET + "/Outbound/docebo/s3_to_raw_error_" + name_suffix, header=True, index=None,quotechar='"',encoding='utf-8', sep=',',quoting=csv.QUOTE_ALL)
    
        #Insert the invalid records in to logs.docebo table
        ##Get invalid rows and insert to logs table
        newdatasource1 = DynamicFrame.fromDF(docebo_coursecompletion_invalid, glueContext, "newdatasource1")
        applymapping1 = ApplyMapping.apply(frame = newdatasource1, mappings = [
            ("Username", "string", "username", "string"),
            ("First name", "string", "firstname", "string"),
            ("Last name", "string", "lastname", "string"),
            ("Course code", "string", "coursecode", "string"),
            ("Course Type", "string", "coursetype", "string"),
            ("Course Name", "string", "coursename", "string"),
            ("First access date", "string", "firstaccessdate", "string"),
            ("Completion Date", "string", "completiondate", "string"),
            ("Status", "string", "status", "string"),
            ("Credits (CEUs)", "string", "credithours", "string"),
            ("DSHS ID", "string", "dshsid", "string"),
            ("CDWA ID", "string", "cdwaid", "string"),
            ("TrainingID", "string", "trainingid", "string"),
            ("DSHS Code", "string", "dshscode", "string"),
            ("filename", "string", "filename", "string"),
            ("filedate", "timestamp", "filedate", "timestamp"),
            ("error_reason", "string", "error_reason", "string")], 
            transformation_ctx = "applymapping1")
        new_df1 = applymapping1.toDF()
        print("Inserting invalid records into logs table")
        mode = "append"
        new_df1.write.jdbc(url=url, table="logs.doceboerrors", mode=mode, properties=properties) 
        
        print("Insert an entry into the log table")
        max_filedate = docebo_coursecompletionfinaldf.first()["filedate"]
        logs_data = [[max_filedate, "glue-docebo-coursecompletions-s3-to-raw", "1"]]
        logs_columns = ['lastprocesseddate', 'processname','success']
        logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
        logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
    
    else:
        print("File has already processed or no records in the file.")
      
    print("Archiving the File.")
    #Archiving Processed files
    #If we have Multiple files of the completions, then one file at time is moved to archive location
    for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/docebo/"):
        if object_summary.key.endswith('csv'):
            filename = object_summary.key
            sourcekey = filename
            targetkey = sourcekey.replace("/raw/", "/archive/")
            copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
            s3bucket.copy(copy_source, targetkey)
            s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
else:
    print("No new file in S3 Bucket for processing!!!!")
    
job.commit()