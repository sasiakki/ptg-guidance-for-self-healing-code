import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import md5,concat_ws,col,current_timestamp,input_file_name
from pyspark.sql.functions import col,when,to_timestamp,regexp_extract
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import IntegerType,LongType
import boto3
import re
import json
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

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/credential/"):
      if object_summary.key.endswith('TXT'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/credential/)(01250_TPCertification_ADSAToTP_)(\d\d\d\d\d\d\d\d_\d\d\d\d\d\d)(.TXT)", object_summary.key).group(3), '%Y%m%d_%H%M%S').date()
        files_list[filename] = filedate

if len(files_list) !=0:
    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key = files_list.get).pop()
    
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    
    # Script for S3 bucket to read file in format 01250_TPCertification_ADSAToTP_XX.TXT
    rawcredentialcdf = glueContext.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": '"',
            "withHeader": True,
            "separator": "|",
            "optimizePerformance": True,
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [sourcepath],
            "recurse": True,
        }
    )

    # Coverting glue dynamic dataframe to spark dataframe
    rawcredentialdf = rawcredentialcdf.toDF()

    rawcredentialdf = rawcredentialdf.withColumn("inputfilename", input_file_name())
    rawcredentialdf = rawcredentialdf.withColumn("filename", regexp_extract(col('inputfilename'), '(s3://)(.*)(/Inbound/raw/credential/)(.*)', 4))
    rawcredentialdf = rawcredentialdf.withColumn("filemodifieddate", to_timestamp(regexp_extract(col('filename'), '(01250_TPCertification_ADSAToTP_)(\d\d\d\d\d\d\d\d_\d\d\d\d\d\d)(.TXT)', 2), "yyyyMMdd_HHmmss"))
    
    rawcredentialdf = rawcredentialdf.select([when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c) for c in rawcredentialdf.columns])

    rawcredentialdf = rawcredentialdf.withColumn("studentid",col("studentid").cast(LongType()))\
            .withColumn("taxid",col("taxid").cast(IntegerType()))\
            .withColumn("providernumber",col("providernumber").cast(LongType()))\
            .withColumn("recordmodifieddate",current_timestamp())\
            .withColumn('hashidkey',md5(concat_ws("",col("studentid"),col("taxid"),col("providernumber"),col("credentialnumber"),col("providernamedshs"),col("providernamedoh"),col("dateofbirth"),col("dateofhire"),col("limitedenglishproficiencyindicator"),col("firstissuancedate"),col("lastissuancedate"),col("expirationdate"),col("credentialtype"),col("credentialstatus"),col("lepprovisionalcredential"),col("lepprovisionalcredentialissuedate"),col("lepprovisionalcredentialexpirationdate"),col("actiontaken"),col("continuingeducationduedate"),col("longtermcareworkertype"),col("excludedlongtermcareworker"),col("paymentdate"),col("credentiallastdateofcontact"),col("preferredlanguage"),col("credentialstatusdate"),col("nctrainingcompletedate"),col("examscheduleddate"),col("examscheduledsitecode"),col("examscheduledsitename"),col("examtestertype"),col("examemailaddress"),col("examdtrecdschedtestdate"),col("phonenum"))))

    # Coverting  spark dataframe to glue dynamic dataframe
    rawcredentialcdf = DynamicFrame.fromDF(rawcredentialdf, glueContext, "rawcredentialcdf")

    # ApplyMapping to match the target table
    rawcredentialcdf_applymapping = ApplyMapping.apply(frame = rawcredentialcdf, mappings = [("studentid", "long", "studentid", "long"),("taxid", "int", "taxid", "int"),("providernumber", "long", "providernumber", "long"),("credentialnumber", "string", "credentialnumber", "string"),("providernamedshs", "string", "providernamedshs", "string"),("providernamedoh", "string", "providernamedoh", "string"),("dateofbirth", "string", "dateofbirth", "string"),("filename", "string", "filename", "string"),("filemodifieddate", "timestamp", "filemodifieddate", "timestamp"), ("dateofhire", "string", "dateofhire", "string"), ("limitedenglishproficiencyindicator", "string", "limitedenglishproficiencyindicator", "string"), ("firstissuancedate", "string", "firstissuancedate", "string"), ("lastissuancedate", "string", "lastissuancedate", "string"), ("expirationdate", "string", "expirationdate", "string"), ("credentialtype", "string", "credentialtype", "string"), ("credentialstatus", "string", "credentialstatus", "string"), ("lepprovisionalcredential", "string", "lepprovisionalcredential", "string"), ("lepprovisionalcredentialissuedate", "string", "lepprovisionalcredentialissuedate", "string"), ("lepprovisionalcredentialexpirationdate", "string", "lepprovisionalcredentialexpirationdate", "string"), ("actiontaken", "string", "actiontaken", "string"), ("continuingeducationduedate", "string", "continuingeducationduedate", "string"), ("longtermcareworkertype", "string", "longtermcareworkertype", "string"), ("excludedlongtermcareworker", "string", "excludedlongtermcareworker", "string"), ("paymentdate", "string", "paymentdate", "string"), ("credentiallastdateofcontact", "string", "credentiallastdateofcontact", "string"), ("preferredlanguage", "string", "preferredlanguage", "string"), ("credentialstatusdate", "string", "credentialstatusdate", "string"), ("nctrainingcompletedate", "string", "nctrainingcompletedate", "string"), ("examscheduleddate", "string", "examscheduleddate", "string"), ("examscheduledsitecode", "string", "examscheduledsitecode", "string"), ("examscheduledsitename", "string", "examscheduledsitename", "string"), ("examtestertype", "string", "examtestertype", "string"), ("examemailaddress", "string", "examemailaddress", "string"), ("examdtrecdschedtestdate", "string", "examdtrecdschedtestdate", "string"), ("phonenum", "string", "phonenum", "string"),("hashidkey","string","hashidkey","string"),("recordmodifieddate","timestamp","recordmodifieddate","timestamp")], transformation_ctx = "rawcredentialcdf_applymapping")
    # Coverting glue dynamic dataframe to spark dataframe
    rawcredential_final_df = rawcredentialcdf_applymapping.toDF()

    # Truncating and loading the processed data
    rawcredential_final_df.write.option("truncate", True).jdbc(
        url=url, table="raw.credential", mode=mode, properties=properties)
    
    print("Insert an entry into the log table")
    max_filedate = rawcredential_final_df.first()["filemodifieddate"]
    logs_data = [[max_filedate, "glue-credentials-doh-s3-to-raw", "1"]]          
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
    
    #Capturing the Schema of the raw.credential
    credential_doh_schema = spark.read.jdbc(url=url, table="raw.credential", properties=properties).schema
    
    # Create a dataframe with expected schema
    rawcredential_final_df = spark.createDataFrame(data = [],schema = credential_doh_schema)
    
    # Truncating and loading the empty data
    rawcredential_final_df.write.option("truncate", True).jdbc(
        url=url, table="raw.credential", mode=mode, properties=properties)





job.commit()
