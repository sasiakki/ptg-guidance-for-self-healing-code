import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import boto3
import json
import re
import pandas as pd
from datetime import datetime
from heapq import nsmallest
from awsglue.utils import getResolvedOptions
from pyspark.sql.functions import *
from datetime import datetime
log_time = datetime.now()

args_account = getResolvedOptions(sys.argv, ["environment_type"])	
environment_type = args_account['environment_type']	
if environment_type == 'dev' :	
    catalog_database = 'postgresrds'	
    catalog_table_prefix = 'b2bdevdb'	
else:	
    catalog_database = 'seiubg-rds-b2bds'	
    catalog_table_prefix = 'b2bds'

    
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
#Getting secrets from secrest manager

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
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')
Isfilepresent=False
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/ip_benefitscontinuation/"):
      if object_summary.key.endswith('csv'):
          filename = object_summary.key
          filenamenew=re.search(r"(Inbound/raw/ip_benefitscontinuation/)(BC_File for_EA_\d\d\.\d\d\.\d\d.csv)", filename).group(2)
          filedate = datetime.strptime(re.search(r"(Inbound/raw/ip_benefitscontinuation/)(BC_File for_EA_)(\d\d\.\d\d\.\d\d)(.csv)", object_summary.key).group(3), '%m.%d.%y').date()
          sourcepath = "s3://"+S3_BUCKET+"/"+filename+""
          benefitsip = spark.read.format("csv").option("header","true").option("inferSchema","false").option("escape","\"").load(f"{sourcepath}")
          benefitsip=benefitsip.withColumn("filedate",lit(filedate)).withColumn("filename",lit(filenamenew))
          benefitsip = benefitsip.dropna(subset=["BG Person ID","Due Date Override","Due Date Override Reason","BC Approved Date"])
          benefitsip = benefitsip.toPandas()
          benefitsip = benefitsip.fillna(value=' ')
    
          if benefitsip.size!=0 :
              benefitsip['BC Approved Date']=pd.to_datetime(benefitsip['BC Approved Date'])
              benefitsip['Due Date Override']=pd.to_datetime(benefitsip['Due Date Override'])
              benefitsip['BG Person ID'] = benefitsip['BG Person ID'].astype('float')
              benefitsip['BG Person ID'] = benefitsip['BG Person ID'].astype('int64')
              print(benefitsip)
              benefitsip_df = spark.createDataFrame(benefitsip)
              benefitsip_df = DynamicFrame.fromDF(benefitsip_df, glueContext, "benefitsip_df")
              ApplyMapping_node2 = ApplyMapping.apply(
              frame=benefitsip_df, 
              mappings=[
              ("BG Person ID", "long", "bgpersonid", "string"),
              ("Employer Requested", "string", "employerrequested", "string"),
              ("First Name", "string", "firstname", "string"),
              ("Last Name", "string", "lastname", "string"),
              ("Email", "string", "email", "string"),
              ("BC Approved Date", "timestamp", "bcapproveddate", "timestamp"),
              ("Due Date Override Reason", "string", "duedateoverridereason", "string"),
              ("Training Name", "string", "trainingname", "string"),
              ("Due Date Override", "timestamp", "duedateoverride", "timestamp"),
              ("filedate", "date", "filedate", "date"),
              ("filename","string","filename","string")
              ], 
              transformation_ctx="ApplyMapping_node2",)
  
              final_df = ApplyMapping_node2.toDF()
              #Truncating and loading the processed data
              final_df.write.option("truncate", False).jdbc(url=url, table="raw.ip_benefitscontinuation", mode="append", properties=properties)
          
              #Archiving Processed files

              sourcekey = filename
              targetkey = sourcekey.replace("/raw/", "/archive/")
              copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
              s3bucket.copy(copy_source, targetkey)
              s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
              Isfilepresent=True
if Isfilepresent == False:
    print("No Files found!!")

#Insert an entry into the log
# WRITE a record with process/execution time to logs.lastprocessed table
logs_data = [[log_time, "glue-benefitscontinuation-s3-raw", "1"]]
logs_columns = ['lastprocesseddate', 'processname','success']
logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= "append", properties= properties)
 
job.commit()
