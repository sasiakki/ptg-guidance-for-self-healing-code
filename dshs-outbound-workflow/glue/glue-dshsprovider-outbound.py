import boto3
import json
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import first
from awsglue.utils import getResolvedOptions
import sys

# Retrieve secrets from AWS Secrets Manager.
secrets_manager_client = boto3.client('secretsmanager')
s3client = boto3.client('s3')
s3resource = boto3.resource('s3')

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'
    


# Get SFTP detaiils from secrets.
try:
      #Accessing the secrets value for S3 Bucket
    s3response = secrets_manager_client.get_secret_value(
        SecretId="{}/b2bds/s3".format(environment_type))
    
    s3_secrets = json.loads(s3response['SecretString'])
    
    s3_bucket = s3_secrets['datafeeds']
    
except Exception as e:
    print(f"Failed to get s3_secrets information from Secrets Manager secret: {e}")
    raise Exception ("Failed to get sftp_secrets ,s3_secrets, database_secrets information from Secrets Manager secret in {}".format(environment_type))


#suffix 
today = datetime.now()
suffix = today.strftime("%Y%m%d_%H%M%S")
print(suffix)

def main():
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session

    dyf = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_outbound_vw_dshsprovider",
    transformation_ctx="dyf",
)
    outboundDF = dyf.toDF()
    pandas_df = outboundDF.toPandas()
    pandas_df.to_csv("s3://"+s3_bucket+"/Outbound/dshsproviders/01250_PROVIDERS_TPTOADSA_"+suffix+"_All.txt", header=None, index=None, sep='|', mode='a')
    
if __name__ == "__main__": 
    main()
