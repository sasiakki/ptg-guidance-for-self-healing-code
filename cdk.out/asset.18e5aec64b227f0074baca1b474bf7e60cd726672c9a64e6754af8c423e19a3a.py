import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
import boto3
import json


#Default JOB arguments
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

#Capturing the current date to append to filename
today = datetime.now()
#suffix = today.strftime("%m_%d_%Y")
suffix = today.strftime("%Y%m%d%H%M%S")

#Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')


#Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']


#Captruting employer info
employer_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_employer").toDF()

employer_pdf = employer_df.toPandas()

#New Useraccount
employer_pdf.to_csv("s3://"+S3_BUCKET+"/Outbound/snowflake/employer/prod_employer_"+suffix+".csv", header=True, index=None, sep=',')


job.commit()
