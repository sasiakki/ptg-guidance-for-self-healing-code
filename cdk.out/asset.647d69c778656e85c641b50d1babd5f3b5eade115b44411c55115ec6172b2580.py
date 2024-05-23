import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import lit,regexp_extract,when,col,current_timestamp,to_timestamp,concat,split
from awsglue.dynamicframe import DynamicFrame
import boto3
import json
import re
from datetime import datetime
from heapq import nsmallest

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
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

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/doh/completed/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/doh/completed/)(HMCC - DSHS Benefit Training Completed File )(\d\d\d\d_\d\d_\d\d_\d\d\d\d\d\d)(.csv)", object_summary.key).group(3), '%Y_%m_%d_%H%M%S').date()
        files_list[filename] = filedate

if len(files_list) !=0:
    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    gluedatasourcedohcompleted = glueContext.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": '"',
            "withHeader": False,
            "separator": ",",
            "optimizePerformance": False,
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [sourcepath],
            "recurse": True,
        }
    )
    #DOH Completed CSV Has top 6 rows has summary information, so skipping first 6 rows
    dohcompleted_pd_df = gluedatasourcedohcompleted.toDF().toPandas()[6:]
    #Reset the index of remaining data
    dohcompleted_pd_df.reset_index(drop=True, inplace=True)
    #Capturing the 1st row after index reset as list of columns new dataset 
    dohcompleted_pd_df.columns=dohcompleted_pd_df.iloc[0].str.replace(' ', '')
    #Skipping the 1st row and captturing the remaining rows
    dohcompleted_pd_df = dohcompleted_pd_df[1:]
    
    if dohcompleted_pd_df.size!=0 :
        
        # convert pandas dataframe to spark dataframe
        dohcompleted_df = spark.createDataFrame(dohcompleted_pd_df)
        
        #Capturing all the necessary columns like filename, filedate and removing blank spaces from dataset
        dohcompleted_df = dohcompleted_df.withColumn("inputfilename", lit(sourcepath))
        dohcompleted_df = dohcompleted_df.withColumn("filename",regexp_extract(col('inputfilename'), '(s3://)(.*)(/Inbound/raw/doh/completed/)(.*)', 4))
        dohcompleted_df = dohcompleted_df.withColumn("filemodifieddate",to_timestamp(regexp_extract(col('filename'), '(HMCC - DSHS Benefit Training Completed File )(\d\d\d\d_\d\d_\d\d_\d\d\d\d\d\d)(.csv)', 2),"yyyy_MM_dd_HHmmss"))
        dohcompleted_df = dohcompleted_df.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in dohcompleted_df.columns])
        
        #capturing the credential number from exesting credential column
        dohcompleted_df = dohcompleted_df.withColumn("credentialnumber", concat(split(col("Credential"), "\\.").getItem(1),split(col("Credential"), "\\.").getItem(2)))
        dohcompleted_df = dohcompleted_df.withColumn("recordmodifieddate",current_timestamp())
        
        #Apply necessary mappings
        newdatasource_dohcompleted = DynamicFrame.fromDF(dohcompleted_df, glueContext, "newdatasource_dohcompleted")
        dohcompleted_applymapping = ApplyMapping.apply(frame = newdatasource_dohcompleted, mappings = [("FileLastName", "string", "filelastname", "string"),("filemodifieddate", "timestamp", "filedate", "timestamp"), ("FileFirstName", "string", "filefirstname", "string"), ("FileReceivedDate", "string", "filereceiveddate", "string"), ("DOHName", "string", "dohname", "string"), ("credentialnumber", "string", "credentialnumber", "string"),("CredentialStatus","string","credentialstatus","string"), ("ApplicationDate", "string", "applicationdate", "string"), ("DateApprovedInstructorCodeandNameUDFUpdated", "string", "dateapprovedinstructorcodeandnameudfupdated", "string"), ("ApprovedInstructorCodeandName", "string", "approvedinstructorcodeandname", "string"),("DateGraduatedfor70Hours","string","dategraduatedfor70hours","string"),("recordmodifieddate","timestamp","recordmodifieddate","timestamp"),("filename","string","filename","string")], transformation_ctx = "dohcompleted_applymapping")

        #Convert to spark dataframe
        dohcompleted_target_df = dohcompleted_applymapping.toDF()
        
        # Truncating and loading the processed data
        dohcompleted_target_df.write.option("truncate",True).jdbc(url=url, table="raw.dohcompleted", mode=mode, properties=properties)

    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()

job.commit()