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
sc = SparkContext.getOrCreate()
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
mode = "append"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/doh/classified/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/doh/classified/)(HMCC - DSHS Benefit Classified File )(\d\d\d\d_\d\d_\d\d_\d\d\d\d\d\d)(.csv)", object_summary.key).group(3), '%Y_%m_%d_%H%M%S').date()
        files_list[filename] = filedate 



if len(files_list) !=0:
    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    gluedatasourcedohclassified = glueContext.create_dynamic_frame.from_options(
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
    #DOH Classified CSV Has top 6 rows has summary information, so skipping first 6 rows
    dohclassified_pd_df = gluedatasourcedohclassified.toDF().toPandas()[6:]
    #Reset the index of remaining data
    dohclassified_pd_df.reset_index(drop=True, inplace=True)
    #Capturing the 1st row after index reset as list of columns new dataset 
    dohclassified_pd_df.columns=dohclassified_pd_df.iloc[0].str.replace(' ', '')
    #Skipping the 1st row and captturing the remaining rows
    dohclassified_pd_df = dohclassified_pd_df[1:]
    
    if dohclassified_pd_df.size!=0:
        datasource1 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource1") 	 
        logslastprocessed = datasource1.toDF().createOrReplaceTempView("vwlogslastprocessed")
        
        # convert pandas dataframe to spark dataframe
        dohclassified_df = spark.createDataFrame(dohclassified_pd_df)
        
        #Capturing all the necessary columns like filename, filedate and removing blank spaces from dataset
        dohclassified_df = dohclassified_df.withColumn("inputfilename", lit(sourcepath))
        dohclassified_df = dohclassified_df.withColumn("filename",regexp_extract(col('inputfilename'), '(s3://)(.*)(/Inbound/raw/doh/classified/)(.*)', 4))
        dohclassified_df = dohclassified_df.withColumn("filemodifieddate",to_timestamp(regexp_extract(col('filename'), '(HMCC - DSHS Benefit Classified File )(\d\d\d\d_\d\d_\d\d_\d\d\d\d\d\d)(.csv)', 2),"yyyy_MM_dd_HHmmss"))
        
        dohclassified_df.createOrReplaceTempView("vwrawdohclassifieddf")
    
        dohclassified_df = spark.sql("""SELECT * FROM vwrawdohclassifieddf where filemodifieddate > (
                                        SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1)
                                                ELSE MAX(lastprocesseddate)
                                                END AS MAXPROCESSDATE
                                        FROM vwlogslastprocessed 
                                        WHERE processname='glue-doh-classified-s3-to-raw' AND success='1')""")
   
        if(dohclassified_df.count() > 0): 
            dohclassified_df = dohclassified_df.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in dohclassified_df.columns])
        
            # Inrecent files we are receving the and Hash(#) symbol in column name so renameing it ro remove symbol  
            dohclassified_df = dohclassified_df.withColumnRenamed("Credential#","Credential")
        
            #capturing the credential number from existing credential column
            dohclassified_df = dohclassified_df.withColumn("credentialnumber", concat(split(col("Credential"), "\\.").getItem(1), split(col("Credential"), "\\.").getItem(2)))
            dohclassified_df = dohclassified_df.withColumn("recordmodifieddate",current_timestamp())
            

            #Apply necessary mappings
            newdatasource_dohclassified = DynamicFrame.fromDF(dohclassified_df, glueContext, "newdatasource_dohclassified")
            dohclassified_applymapping = ApplyMapping.apply(frame = newdatasource_dohclassified, mappings = [("FileLastName", "string", "filelastname", "string"),("filemodifieddate", "timestamp", "filedate", "timestamp"), ("FileFirstName", "string", "filefirstname", "string"), ("FileReceivedDate", "string", "filereceiveddate", "string"), ("DOHName", "string", "dohname", "string"), ("credentialnumber", "string", "credentialnumber", "string"),("CredentialStatus","string","credentialstatus","string"), ("ApplicationDate", "string", "applicationdate", "string"), ("Datedshsbenefitpaymentudfupdated", "string", "datedshsbenefitpaymentudfupdated", "string"),("recordmodifieddate","timestamp","recordmodifieddate","timestamp"),("filename","string","filename","string")], transformation_ctx = "dohclassified_applymapping")

            #Convert to spark dataframe
            dohclassified_target_df = dohclassified_applymapping.toDF()
            
            # Truncating and loading the processed data
            dohclassified_target_df.write.jdbc(url=url, table="raw.dohclassified", mode=mode, properties=properties)
            
            print("Insert an entry into the log table") 
            max_filedate = spark.sql("select to_timestamp(max(filemodifieddate)) as filedate from vwrawdohclassifieddf")
            max_filedate = max_filedate.first()["filedate"]
            logs_data = [[max_filedate, "glue-doh-classified-s3-to-raw", "1"]] 		 
            logs_columns = ['lastprocesseddate', 'processname','success'] 		 
            logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
            logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
            
        else:
            print("File has already processed or no records in the file.")

    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()


job.commit()