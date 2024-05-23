import sys 
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import input_file_name,when,col,regexp_extract,to_date, to_timestamp
from awsglue.dynamicframe import DynamicFrame
import boto3
import re
import json
from datetime import datetime
from heapq import nsmallest
from pyspark.sql.types import StructField,StringType,StructType

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

 # Default Job Arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

datasource1 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource1")        
logslastprocessed = datasource1.toDF().createOrReplaceTempView("vwlogslastprocessed")

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/ospi/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/ospi/)(TP-O-OSPI-)(\d\d\d\d-\d\d-\d\d)(.csv)", object_summary.key).group(3), '%Y-%m-%d').date()
        files_list[filename] = filedate

if len(files_list) !=0:
    
    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    
   # Script generated for node Data Catalog table
    
    rawospicredentialcdf = glueContext.create_dynamic_frame.from_options(
        format_options={"quoteChar": '"', "withHeader": True, "separator": ",","inferSchema": False},
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [sourcepath],
            "recurse": True,
        },
        transformation_ctx="rawospicredentialcdf",
    )
    
    # Coverting glue dynamic dataframe to spark dataframe
    rawospicredentialdf = rawospicredentialcdf.toDF()
    
    #Applying Enrichment Data
    rawospicredentialdf = rawospicredentialdf.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in rawospicredentialdf.columns])\
                         .withColumn("inputfilename", input_file_name())\
                         .withColumn("filename", regexp_extract(col('inputfilename'), '(s3://)(.*)(/Inbound/raw/ospi)/(.*)', 4))\
                         .withColumn("filedate",to_date(regexp_extract(col('filename'), '(TP-O-OSPI-)(\d\d\d\d-\d\d-\d\d)(.csv)', 2),"yyyy-MM-dd"))

    rawospicredentialdf.createOrReplaceTempView("vwrawospicredentialdf")
    
    rawospicredentialdf = spark.sql("""SELECT * FROM vwrawospicredentialdf where filedate > (
                                        SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1)
                                                ELSE MAX(lastprocesseddate)
                                                END AS MAXPROCESSDATE
                                        FROM vwlogslastprocessed 
                                        WHERE processname='glue-credentials-ospi-s3-to-raw' AND success='1')""")
   
    if(rawospicredentialdf.count() > 0):         
        print("New file is processing")          
        print("Total record count: {0} ".format(rawospicredentialdf.count()))        
                         
        #Coverting  spark dataframe to glue dynamic dataframe
        rawospicredentialcdf = DynamicFrame.fromDF(rawospicredentialdf, glueContext, "rawospicredentialcdf")
        
        # ApplyMapping to match the target table
        rawospicredentialcdf_applymapping = ApplyMapping.apply(
            frame=rawospicredentialcdf,
            mappings=[
                ("personid", "string", "personid", "string"),
                ("employer", "string", "employer", "string"),
                ("firstname", "string", "firstname", "string"),
                ("middlename", "string", "middlename", "string"),
                ("lastname", "string", "lastname", "string"),
                ("birthdate", "string", "birthdate", "string"),
                ("credential", "string", "credentialnumber", "string"),
                ("credential type", "string", "credentialtype", "string"),
                ("credential status", "string", "credentialstatus", "string"),
                ("first issuance", "string", "firstissuancedate", "string"),
                ("expiration date", "string", "expirationdate", "string"),
                ("filename", "string", "filename", "string"),
                ("filedate", "date", "filedate", "string")
         ],
            transformation_ctx="rawospicredentialcdf_applymapping",
        )
        
        # Coverting glue dynamic dataframe to spark dataframe
        rawcredential_final_df = rawospicredentialcdf_applymapping.toDF()
        
        # Truncating and loading the processed data
        mode = "append"
        url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
        properties = {"user": B2B_USER, "password": B2B_PASSWORD,
                      "driver": "org.postgresql.Driver"}
        rawcredential_final_df.write.jdbc(
            url=url, table="raw.credential_ospi", mode=mode, properties=properties)
        
        print("Insert an entry into the log table") 
        max_filedate = spark.sql("select to_timestamp(max(filedate)) as filedate from vwrawospicredentialdf")
        max_filedate = max_filedate.first()["filedate"]
        logs_data = [[max_filedate, "glue-credentials-ospi-s3-to-raw", "1"]]         
        logs_columns = ['lastprocesseddate', 'processname','success']        
        logs_dataframe = spark.createDataFrame(logs_data, logs_columns)          
        mode = 'append'          
        logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
        
    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(""+S3_BUCKET+"", sourcekey).delete() 
    
    
else:
    print("File has already processed or no records in the file.")
    # Create an credential_ospi_columns schema
    credential_ospi_columns = StructType([StructField('personid',StringType(), True),
                        StructField('employer',StringType(), True),
                        StructField('firstname',StringType(), True),
                        StructField('middlename',StringType(), True),
                        StructField('lastname',StringType(), True),
                        StructField('birthdate',StringType(), True),
                        StructField('credentialnumber',StringType(), True),
                        StructField('credentialtype',StringType(), True),
                        StructField('firstissuancedate',StringType(), True),
                        StructField('expirationdate',StringType(), True),
                        StructField('filename',StringType(), True),
                        StructField('filedate',StringType(), True)
                        ])
    
    # Create a dataframe with expected schema
    rawcredential_final_df = spark.createDataFrame(data = [],schema = credential_ospi_columns)
    # Truncating and loading the empty data
    mode = "overwrite"
    url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
    properties = {"user": B2B_USER, "password": B2B_PASSWORD,
                  "driver": "org.postgresql.Driver"}
    rawcredential_final_df.write.option("truncate", True).jdbc(
        url=url, table="raw.credential_ospi", mode=mode, properties=properties)
    
job.commit()