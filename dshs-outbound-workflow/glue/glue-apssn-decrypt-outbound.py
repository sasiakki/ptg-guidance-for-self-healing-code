import sys
from awsglue.transforms import *
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
import boto3
import json
from cryptography.fernet import Fernet
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from awsglue.utils import getResolvedOptions
import sys

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
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
S3_BUCKET = s3_secrets['datafeeds']

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


fernetresponse = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/glue/fernet'
)

fernetsecrets = json.loads(fernetresponse['SecretString'])
key = fernetsecrets['key']
f = Fernet(key)

# Define decrypt user defined function 
def decrypt_val(cipher_text,MASTER_KEY):
    from cryptography.fernet import Fernet
    f = Fernet(MASTER_KEY)
    clear_val=f.decrypt(cipher_text.encode()).decode()
    return clear_val
    
# Register UDF's
decrypt = udf(decrypt_val, StringType())

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1651673286473 = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_prod_person",
    transformation_ctx="AWSGlueDataCatalog_node1651673286473",
)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1651673320896 = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_staging_idcrosswalk",
    transformation_ctx="AWSGlueDataCatalog_node1651673320896",
)

# Script generated for node AWS Glue Data Catalog
AWSGlueDataCatalog_node1651673351240 = glueContext.create_dynamic_frame.from_catalog(
     database=catalog_database,
    table_name=catalog_table_prefix+"_prod_employmentrelationship",
    transformation_ctx="AWSGlueDataCatalog_node1651673351240",
)

idcrosswalkdf = AWSGlueDataCatalog_node1651673320896.toDF()
employmentrelationshipdf = AWSGlueDataCatalog_node1651673351240.toDF()

idcrosswalkdf = idcrosswalkdf.withColumn("fullssn",decrypt("fullssn",lit(key)))

idcrosswalkdf.createOrReplaceTempView("idcrosswalk")
employmentrelationshipdf.createOrReplaceTempView("employmentrelationship")

joindf = spark.sql("select Distinct i.personid,i.fullssn from idcrosswalk i left join employmentrelationship emp \
                    on i.personid = emp.personid and emp.role = 'CARE'\
                    where length(i.fullssn) >= 7 and i.personid is not null")
                    
#Add leading 0's to 7 and 8 digit SSN
joindf = joindf.withColumn("fullssn", format_string("%09d", col("fullssn").cast('int')))

print("joindf:")                    
joindf.show(truncate = False)
today = datetime.now()
suffix = today.strftime("%Y%m%d_%H%M%S")

print(suffix)

pandas_df = joindf.toPandas()
pandas_df['personid'] = pandas_df['personid'].astype(int)

pandas_df.head()
pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/dshs/01250_APSSN_TPTOADSA_"+suffix+"_All.txt", header=False, index=False, sep='|')


job.commit()
