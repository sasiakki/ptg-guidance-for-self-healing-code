import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame
import boto3
import json
import pandas as pd
import csv


args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

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

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,
              "driver": "org.postgresql.Driver"}

# Multiple files of the completions can be processed in same time
sourcepath = "s3://"+S3_BUCKET+"/Inbound/raw/cornerstone/"


print("************Starting glue job execution**********************")

rawcornerstonecompletions = spark.read.format("csv").option("header","true").option("inferSchema","false").option("escape","\"").load(f"{sourcepath}")
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
print("Total record count: {0} ".format(rawcornerstonecompletions.count()))
rawcornerstonecompletions = rawcornerstonecompletions.withColumn("filename", input_file_name())
rawcornerstonecompletions = rawcornerstonecompletions.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/Inbound/raw/cornerstone/)(.*)', 4))
rawcornerstonecompletions = rawcornerstonecompletions.withColumn("filedate",to_date(regexp_extract(col("filenamenew"),r'\d{2}\d{2}\d{2}',0),'MMddyy'))
    
# marking empty columns as null's
rawcornerstonecompletions = rawcornerstonecompletions.select([when(col(c)=="",None).otherwise(col(c)).alias(c) for c in rawcornerstonecompletions.columns])

#Removing the duplicates based on learner id and class id (course name) and marking eny blank values as nulls
rawcornerstonecompletions_valid = rawcornerstonecompletions.dropDuplicates(['BG Person ID', 'Course Title'])

# Check if the personid is has only digits, if not making them as null
rawcornerstonecompletions_valid = rawcornerstonecompletions_valid.filter(col("BG Person ID").rlike("""^[0-9]+$""")).filter(col("Completion Date").isNotNull()).filter(col("Course Title").isNotNull()).filter(col("Status") == "Passed")
rawcornerstonecompletions_valid = rawcornerstonecompletions_valid.filter(to_date(col("Completion Date"),'MM/dd/yy').isNotNull())
#rawcornerstonecompletions_valid.show(2,vertical=True)

# Filtering the rows feilds where combination BG Person ID, Course Title,Completed Date is not empty
#rawcornerstonecompletions_valid = rawcornerstonecompletions_valid.filter(col("BG Person ID").isNotNull() & col("Course Title").isNotNull() & col("Completion Date").isNotNull() ).filter(col("Status") == "Passed")
#rawcornerstonecompletions_valid.show(2)
print("Valid record count: {0} ".format(rawcornerstonecompletions_valid.count()))

#Extracting the invalid records 
rawcornerstonecompletions_invalid = rawcornerstonecompletions.subtract(rawcornerstonecompletions_valid)
print("Invalid record count: {0} ".format(rawcornerstonecompletions_invalid.count()))


rawcornerstonecompletions_valid = rawcornerstonecompletions_valid.withColumn('Date Of Birth', to_date('Date Of Birth','MM/dd/yyyy')).withColumn('Completion Date',to_timestamp("Completion Date",'MM/dd/yy hh:mm:ss aa')) \
                            .withColumn('Completed Date',to_timestamp("Completed Date",'MM/dd/yy hh:mm:ss aa')).withColumn('Registration Date',to_timestamp("Registration Date",'MM/dd/yy hh:mm:ss aa')) \
                            .withColumn('Begin Date',to_timestamp("Begin Date",'MM/dd/yy hh:mm:ss aa')).withColumn('Last Active Date',to_timestamp("Last Active Date",'MM/dd/yy hh:mm:ss aa'))


rawcornerstonecompletions_catalog = DynamicFrame.fromDF(rawcornerstonecompletions_valid, glueContext, "rawcornerstonecompletions_catalog")

# Script Apply Mapping for Cornerstone completions as per target table
rawcornerstonecompletions_targetmapping = ApplyMapping.apply(
    frame=rawcornerstonecompletions_catalog,
    mappings=[
        ("Offering Title", "string", "offering_title", "string"),
        ("Course Title", "string", "course_title", "string"),
        ("Student First Name", "string", "user_first_name", "string"),
        ("Student Last Name", "string", "user_last_name", "string"),
        ("Student Email", "string", "user_email", "string"),
        ("Last Active Date", "timestamp", "last_login_date", "timestamp"),
        ("Course Type", "string", "course_type", "string"),
        ("BG Person ID", "choice", "bg_person_id", "choice"),
        ("Date Of Birth", "date", "date_of_birth", "date"),
        ("Phone Number", "string", "phone_number", "string"),
        ("Street 1", "string", "street_1", "string"),
        ("Street 2", "string", "street_2", "string"),
        ("City", "string", "city", "string"),
        ("State/Province", "string", "state", "string"),
        ("Postal Code", "string", "postal_code", "string"),
        ("Registration Date", "timestamp", "registered_date", "timestamp"),
        ("Begin Date", "timestamp", "begin_date", "timestamp"),
        ("Completed Date", "timestamp", "completed_date", "timestamp"),
        ("Grade", "string", "grade_percentage", "string"),
        ("Status", "string", "status", "string"),
        ("Completion Percentage", "string", "completion_percentage", "string"),
        ("Completion Date", "timestamp", "completion_date", "timestamp"),
        ("filenamenew", "string", "filename", "string"),
        ("filedate", "date", "filedate", "date")
    ],
    transformation_ctx="rawcornerstonecompletions_targetmapping",
)

# Coverting glue dynamic dataframe to spark dataframe
rawcornerstonecompletionsfinaldf = rawcornerstonecompletions_targetmapping.toDF()

# Truncating and loading the processed data
rawcornerstonecompletionsfinaldf.write.option("truncate", True).jdbc(
    url=url, table="raw.cornerstone_completion", mode=mode, properties=properties)

#Saving Invalid records and exporting to S3 bucket
if(rawcornerstonecompletions_invalid.count() > 0):
    print("Exporting and Saving invalid records")
    rawcornerstonecompletions_invalid = rawcornerstonecompletions_invalid.withColumn("error_reason",when(col("BG Person ID").isNull(),"PersonID is not Valid")
                                                                 .when(col("Completion Date").isNull(),"Completion date is not valid")
                                                                 .when(to_date(col("Completion Date"),'MM/dd/yy').isNull(),"Completion date is not valid")
                                                                 .when(col("Course Title").isNull(),"CourseID is not valid")
                                                                 .when(col("BG Person ID") == "0","PersonID is not Valid")
                                                                 .when(col("Status") != "Passed","Status is not Valid")
                                                                 .when(col("BG Person ID").isNotNull(),"PersonID is not Valid"))
        
    name_suffix = rawcornerstonecompletions_invalid.select("filenamenew").distinct().limit(1).collect()
    name_suffix = name_suffix[0].filenamenew
    print(name_suffix)
    rawcornerstonecompletions_invalid = rawcornerstonecompletions_invalid.drop("filename")
    rawcornerstonecompletions_invalid = rawcornerstonecompletions_invalid.withColumnRenamed("filenamenew","filename")
    #rawcornerstonecompletions_invalid.show(2,vertical=True)
    pandas_df = rawcornerstonecompletions_invalid.toPandas()
    print("Exporting to S3 bucket")
    # Export the invalid records to a S3 bucket
    pandas_df.to_csv("s3://"+ S3_BUCKET + "/Outbound/cornerstone/s3_to_raw_error_" + name_suffix, header=True, index=None,quotechar='"',encoding='utf-8', sep=',',quoting=csv.QUOTE_ALL)
    
    #Insert the invalid records in to logs.cornerstoneerrors table
    ##Get invalid rows and insert to logs table
    newdatasource1 = DynamicFrame.fromDF(rawcornerstonecompletions_invalid, glueContext, "newdatasource1")
    applymapping1 = ApplyMapping.apply(frame = newdatasource1, mappings = [("Student First Name", "string", "student_first_name", "string"),
        ("Student Last Name", "string", "student_last_name", "string"),
        ("Offering Title", "string", "offering_title", "string"),
        ("Course Title", "string", "course_title", "string"),
        ("Student Email", "string", "student_email", "string"),
        ("Registration Date", "string", "registered_date", "string"),
        ("Begin Date", "string", "begin_date", "string"),
        ("Completion Date", "string", "completion_date", "string"),
        ("Last Active Date", "string", "last_active_date", "string"),
        ("Grade", "string", "grade", "string"),
        ("Status", "string", "status", "string"),
        ("Completion Percentage", "string", "completion_percentage", "string"),
        ("Completed Date", "string", "completed_date", "string"),
        ("Course Type", "string", "course_type", "string"),
        ("BG Person ID", "choice", "bg_person_id", "choice"),
        ("Date Of Birth", "date", "date_of_birth", "date"),
        ("Phone Number", "string", "phone_number", "string"),
        ("Street 1", "string", "street_1", "string"),
        ("Street 2", "string", "street_2", "string"),
        ("City", "string", "city", "string"),
        ("State/Province", "string", "state", "string"),
        ("Postal Code", "string", "postal_code", "string"),
        ("filename", "string", "filename", "string"),
        ("filedate", "date","filedate", "date"),
        ("error_reason", "string", "error_reason", "string")], 
            transformation_ctx = "applymapping1")
    new_df1 = applymapping1.toDF()
    print("Inserting invalid records into logs table")
    mode = "append"
    new_df1.write.jdbc(url=url, table="logs.cornerstoneerrors", mode=mode, properties=properties)    


#Archiving Processed files
#If we have Multiple files of the completions, then one file at time is moved to archive location
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/cornerstone/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        sourcekey = filename
        targetkey = sourcekey.replace("/raw/", "/archive/")
        copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
        s3bucket.copy(copy_source, targetkey)
        s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()

job.commit()
print("************Completed glue job execution**********************")