import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col,regexp_replace,date_format,trim,concat_ws,split,to_timestamp,when,concat,lit,to_date
from awsglue.dynamicframe import DynamicFrame
import boto3
import json
from datetime import datetime

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'
    
# Default JOB arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

#Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

#Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId = environment_type+'/b2bds/rds/system-pipelines'
)

database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

#Capture the full credentials data from raw.credential_delta table
raw_credential_delta_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name= catalog_table_prefix+"_raw_credential_delta",
).toDF()

#Capture the credentials count from staging.personhistory table
person_history_doh = glueContext.create_dynamic_frame.from_catalog(database=catalog_database,table_name= catalog_table_prefix+"_staging_personhistory", transformation_ctx = "person_history_doh").toDF().filter(col("sourcekey").like('CRED-%'))

#When staging.personhistory table has no credentials data then publish full data to personhistory
#Otherwise publish only the delta data
if person_history_doh.count() != 0 : 
    raw_credential_delta_df = raw_credential_delta_df.filter(col("audit")=="New")
 
 
#Filtering out NA records
raw_credential_delta_df = raw_credential_delta_df.filter(col("credentialtype") != 'NA')

# providernamedoh is used for spliting the person name as firstname,middlename,lastname
# If this empty then it cannot be used for person mastering 
#raw_credential_delta_df = raw_credential_delta_df.filter(col("providernamedoh").isNotNull())

# Preparing the source key for credentials as 'CRED-credentialnumber'
raw_credential_delta_df =raw_credential_delta_df.withColumn("sourcekey",concat(lit("CRED-"),raw_credential_delta_df.credentialnumber))

#dateofbirth to check for futuredate and person age <18 years
raw_credential_delta_df = raw_credential_delta_df.withColumn("new_dob",raw_credential_delta_df.dateofbirth.cast('string'))\
                            .withColumn("new_dob",to_date(col("new_dob"),"MM/dd/yyyy"))\
                            .withColumn("new_dob",date_format(col("new_dob"),"yyyy-MM-dd"))


#providernamedoh is used for spliting the person name as firstname,middlename,lastname
raw_credential_delta_df = raw_credential_delta_df.withColumn("providernamedoh",regexp_replace(trim(col('providernamedoh')),'\s+',' '))\
  .withColumn("firstname",split((col('providernamedoh')), '\s')[1])\
  .withColumn("middlename",concat_ws(" ",split(col('providernamedoh'), '\s')[2],split(col('providernamedoh'), '\s')[3],split(col('providernamedoh'), '\s')[4]))\
  .withColumn("lastname",split((col('providernamedoh')), '\s')[0])\
  .withColumn("middlename",when(col('middlename')=="",None).otherwise(trim(col('middlename'))))\
  .withColumn("firstname",when(col('firstname')=="",None).otherwise(trim(col('firstname'))))\
  .withColumn("lastname",when(col('lastname')=="",None).otherwise(trim(col('lastname'))))

#Converting hiredate to accurate target format
raw_credential_delta_df = raw_credential_delta_df.withColumn("hiredate", to_timestamp(col("dateofhire").cast('string'), 'MM/dd/yyyy'))

#Filtering data when firstname, lastname and new_dob is empty                                       
#raw_credential_delta_df = raw_credential_delta_df.where("firstname is not null and lastname is not null and new_dob is not null")
# In case of OSPI Credentials StudentID is the accurate , But not for the DOH Credentials
raw_credential_delta_df.createOrReplaceTempView("credential_delta")

# Capture only personid for OSPI Credentials
raw_credential_delta_df = spark.sql("""
          select
                case WHEN credentialtype = 'OSPI' then personid ELSE NULL END AS personid
                ,firstname
                ,middlename
                ,lastname
                ,hiredate
                ,sourcekey
                ,credentialnumber
                ,new_dob
                ,filemodifieddate 
          from credential_delta
          """)

raw_credential_delta_df.show()

raw_credential_delta_df = DynamicFrame.fromDF(raw_credential_delta_df, glueContext, "raw_credential_delta_df")

mappings_transform = ApplyMapping.apply(frame = raw_credential_delta_df, mappings = [("personid", "long", "personid", "long"),("firstname", "string", "firstname", "string"),("middlename", "string", "middlename", "string"),("lastname", "string", "lastname", "string"),("sourcekey", "string", "sourcekey", "string"),("credentialnumber", "string", "credentialnumber", "string"),("new_dob", "string", "dob", "string"),("hiredate", "timestamp", "hiredate", "timestamp"),("filemodifieddate", "timestamp", "filemodifieddate", "date")], transformation_ctx = "mappings_transform")

target_select_transform = SelectFields.apply(frame = mappings_transform, paths = ["personid","firstname","middlename","lastname","sourcekey","credentialnumber","dob","hiredate","filemodifieddate"], transformation_ctx = "target_select_transform")

resolvechoice3 = ResolveChoice.apply(frame = target_select_transform, choice = "MATCH_CATALOG", database=catalog_database,
    table_name= catalog_table_prefix+"_staging_personhistory", transformation_ctx = "resolvechoice3")

resolvechoice4 = DropNullFields.apply(frame = resolvechoice3,  transformation_ctx = "resolvechoice4")

#Script generated for node PostgreSQL
glueContext.write_dynamic_frame.from_catalog(
    frame=resolvechoice4,
    database=catalog_database,
    table_name= catalog_table_prefix+"_staging_personhistory"
)

print("Insert an entry into the log table")
max_filedate = datetime.now()
logs_data = [[max_filedate, "glue-credentials-delta-raw-to-staging-personhistory", "1"]]
logs_columns = ['lastprocesseddate', 'processname','success']
logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
mode = 'append'
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
    
    
job.commit()