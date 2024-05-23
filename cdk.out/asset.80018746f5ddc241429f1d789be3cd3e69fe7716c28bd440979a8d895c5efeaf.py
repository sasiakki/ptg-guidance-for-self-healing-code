import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3
from pyspark.sql.functions import when,col
import json


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



# Read the new course catalog file after placing it in the s3 bucket
catalog_df = spark.read.option("header","true").option("delimiter", ",").option("encoding", "UTF-8").csv("s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/course_catalog/coursecatalog_01302023.csv")

# Pick only the columns that need to be pushed to db

catalog_df = catalog_df[['Course Title','HOURS','Program Number','Course Type','Language','Version','Course ID','DSHS Course ID','Program Type','STATUS']]

# List the columns to rename and new column names from the matching criteria

cols_to_rename = ['Course Title','HOURS','Program Number','Course Type','Language','Version','Course ID','DSHS Course ID','Program Type','STATUS']
new_cols = ['coursename','credithours','trainingprogramcode','coursetype','courselanguage','courseversion','courseid','dshscourseid','trainingprogramtype','status']

# Rename the existing columns to the new columns

for i in range(0, len(cols_to_rename)):
    catalog_df = catalog_df.withColumnRenamed(cols_to_rename[i],new_cols[i])

# Convert the column type to string

for column in catalog_df.columns:
    catalog_df = catalog_df.withColumn(column, catalog_df['`{}`'.format(column)].cast('string'))


# from pyspark.sql.functions import when
catalog_df = catalog_df.withColumn("trainingprogramtype",
       when(col("trainingprogramcode") == "201", "Basic Training 70")
      .when(col("trainingprogramcode") == "202", "Basic Training 30")
      .when(col("trainingprogramcode") == "203", "Basic Training 9")
      .when(col("trainingprogramcode") == "204", "Basic Training 7")
      .otherwise(col("trainingprogramtype"))
      )    
    
# Drop duplicates, drop null rows
# Drop rows where coursename, courseid,credithours,trainingprogramcode,trainingprogramtype are null
    
catalog_df = catalog_df.dropDuplicates()
catalog_df = catalog_df.na.drop("all")
catalog_df = catalog_df.na.drop(subset=["coursename"])
catalog_df = catalog_df.na.drop(subset=["courseid"])
catalog_df = catalog_df.na.drop(subset=["credithours"])
catalog_df = catalog_df.na.drop(subset=["trainingprogramcode"])
catalog_df = catalog_df.na.drop(subset=["trainingprogramtype"])

# Create a filter for thouse courseid's which are present more than once
# Remove the next 5 rows - run from catalog_df.write if the above filter is not to be applied

# temp_df = catalog_df.groupBy('courseid').count()
# temp_df = temp_df[temp_df['count'] == 1]
# x = temp_df.select('courseid').collect()
# x_array = [ row.courseid for row in x]
# catalog_df = catalog_df.where(col('courseid').isin(x_array))

# Write the final spark dataframe to db by truncating 

catalog_df.write.option("truncate",True).jdbc(url=url, table="prod.coursecatalog", mode=mode, properties=properties)