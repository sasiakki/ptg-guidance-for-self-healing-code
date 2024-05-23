import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.functions import col,when,input_file_name,regexp_extract,to_timestamp,coalesce,to_date
import boto3
import json
import re
import pandas as pd
import csv
from datetime import datetime
from heapq import nlargest

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Setting the timeParserPolicy as legacy for handling multiple types of date formats received in qualtrics responses
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

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
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/qualtrics/O&SCompletion/"):
      if object_summary.key.endswith('csv'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(r"(Inbound/raw/qualtrics/O&SCompletion/)(O&SCompletion)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)", object_summary.key).group(3), '%Y%m%d%H%M%S').date()
        files_list[filename] = filedate

if len(files_list) !=0:

    # For Qualtrics, we always load the full file data for every run, capturing the responseid of the pervious run to differentiate the old and new records . 
    # isDelta flag  is marked as true for new responseid not existing in data store and false for otherwise 
    agencypersonospreviousdf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_os_qual_agency_person", transformation_ctx = "agencypersonospreviousdf")
    agencypersonospreviousdf.toDF().select("responseid").createOrReplaceTempView("agencypersonospreviousdf")

    print("AGENCY PERSON PREVIOUS DF")
    spark.sql(""" select * from agencypersonospreviousdf """).show()
									 
    ## B2BDS-1385: loglast DF
    logslastprocesseddf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "logsdf")
    logslastprocesseddf = logslastprocesseddf.toDF().createOrReplaceTempView("logslastprocessed")

    # N Largesr values in dictionary (N=1)(Values are dates and capturing the latest date) Using nlargest
    processingfilekey = nlargest(1, files_list, key = files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""
    #sourcepath = "s3://"+S3_BUCKET+"/Inbound/raw/qualtrics/O&SCompletion/"
    agencypersonosdf = glueContext.create_dynamic_frame.from_options(
        format_options={
            "quoteChar": '"',
            "withHeader": True,
            "separator": ",",
            "optimizePerformance": True,
        },
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [sourcepath],
            "recurse": True,
        },
        transformation_ctx="agencypersonosdf",
    )
    # Capturing the processing file name, date and marking empty columns as null's 
    agencypersonosdf = agencypersonosdf.toDF().withColumn("filename", input_file_name())
    agencypersonosdf = agencypersonosdf.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/Inbound/raw/qualtrics/O&SCompletion/)(.*)', 4))
    agencypersonosdf = agencypersonosdf.withColumn("filemodifieddate",to_timestamp(regexp_extract(col('filenamenew'), '(O&SCompletion)(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)', 2),"yyyyMMddHHmmss"))
    agencypersonosdf = agencypersonosdf.select([when(col(c)==" ",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in agencypersonosdf.columns])
   
    ## B2BDS-1385: Insert into raw table only if new file filemodifieddate > lastprocesseddate
    agencypersondf = agencypersonosdf.createOrReplaceTempView("s3oscompletiondata")
    agencypersondf = spark.sql("""SELECT * FROM s3oscompletiondata WHERE filemodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                  END AS MAXPROCESSDATE FROM logslastprocessed  WHERE processname='glue-qualtrics-os-completion-s3-to-raw' AND success='1')""")
    
    agencypersonosdf = agencypersonosdf.withColumn("Q13", coalesce(*[to_date("Q13", f) for f in ("MM/dd/yyyy","MM-dd-yyyy", "yyyy-MM-dd","MMddyyyy")]))

    ## B2BDS-1385: the if-else condition based on agencypersonosdf.count() > 0
    if (agencypersonosdf.count() > 0):
        agencypersonosdf_valid = agencypersonosdf.filter(col("Q5_8").rlike("""^[0-9]+$""")).filter(col("Q13").isNotNull()).filter(col("Finished") == "1").filter(col("Q5_8").isNotNull()).filter(col("Q5_8") != "0").filter(col("Q13") < current_date())
        
        #Extracting the invalid records 
        agencypersonos_invaliddf = agencypersonosdf.subtract(agencypersonosdf_valid)
        
        agencypersonos_invaliddf = agencypersonos_invaliddf.withColumn("error_reason",when(col("Q5_8").isNull(),"PersonID is not Valid")
                                                                    .when(col("Q13").isNull(),"Completion date is not valid")
                                                                    .when(to_date(col("Q13"),'MM/dd/yy').isNull(),"Completion date is not valid")
                                                                    .when(col("Q5_8") == "0","PersonID is not Valid")
                                                                    .when(col("Finished") != "1","Finished status is not Valid")
                                                                    .when(col("Q5_8").isNull(),"PersonID is not Valid")
                                                                    .when(col("Q13")> current_date(),"Completion date in future"))
                        
            
        agencypersonos_invaliddf = agencypersonos_invaliddf.drop("filename")
        agencypersonos_invaliddf = agencypersonos_invaliddf.withColumnRenamed("filenamenew","filename") \
                                                        .withColumnRenamed("Q5_8","PersonID") \
                                                        .withColumnRenamed("Q13","completeddate") \
                                                        .withColumnRenamed("Q4","employername") \
                                                        .withColumnRenamed("Q2_1","agency_firstname")\
                                                        .withColumnRenamed("Q2_2","agency_lastname")\
                                                        .withColumnRenamed("Q2_3","agency_email")\
                                                        .withColumnRenamed("Q5_1","person_firstname") \
                                                        .withColumnRenamed("Q5_2","person_lastname") \
                                                        .withColumnRenamed("Q5_3","person_dob") \
                                                        .withColumnRenamed("Q5_4","person_phone")                                                       
        
        #Saving Invalid records and exporting to S3 bucket
        if(agencypersonos_invaliddf.count() > 0):
            print("Exporting and Saving invalid records")
            agencypersonos_invaliddf.show()
            pandas_df = agencypersonos_invaliddf.toPandas()
            print("Exporting to S3 bucket")
            # Export the invalid records to a S3 bucket
            pandas_df.to_csv("s3://"+ S3_BUCKET + "/Outbound/qualtrics/errorlog/s3_to_raw_error_" + processingfilekey, header=True, index=None,quotechar='"',encoding='utf-8', sep=',',quoting=csv.QUOTE_ALL)
        
            agency_invalid_os_records_datasource = DynamicFrame.fromDF(agencypersonos_invaliddf, glueContext, "newdatasource1")
            agency_invalid_os_records_mapping = ApplyMapping.apply(frame = agency_invalid_os_records_datasource, mappings = [("StartDate", "string", "startdate", "string"),
                    ("EndDate", "string", "enddate", "string"),       
                    ("Status", "string", "status", "string"),
                    ("IPAddress", "string", "ipaddress", "string"),
                    ("Progress", "string", "progress", "string"), 
                    ("Duration (in seconds)", "string", "duration_in_seconds", "string"),
                    ("RecordedDate", "string", "recordeddate", "string"), 
                    ("Finished", "string", "finished", "string"), 
                    ("ResponseId", "string", "responseid", "string"), 
                    ("LocationLatitude", "string", "locationlatitude", "string"), 
                    ("LocationLongitude", "string", "locationlongitude", "string"),
                    ("DistributionChannel", "string", "distributionchannel", "string"), 
                    ("UserLanguage", "string", "userlanguage", "string"),
                    ("Q_RecaptchaScore", "string", "q_recaptchascore", "string"), 
                    ("agency_firstname", "string", "agency_firstname", "string"),
                    ("agency_lastname", "string", "agency_lastname", "string"), 
                    ("agency_email", "string", "agency_email", "string"),
                    ("employername", "string", "employername", "string"),
                    ("person_firstname", "string", "person_firstname", "string"), 
                    ("person_lastname", "string", "person_lastname", "string"), 
                    ("person_dob", "string", "person_dob", "string"),
                    ("person_phone", "string", "person_phone", "string"),
                    ("PersonID", "string", "person_id", "string"),
                    ("completeddate", "string", "os_completion_date", "string"),       
                    ("filename", "string", "filename", "string"),
                    ("filemodifieddate", "timestamp", "filemodifieddate", "timestamp"),
                    ("error_reason", "string", "error_reason", "string")], 
                                transformation_ctx = "agency_invalid_os_records_mapping")
            agency_invalid_os_records_df = agency_invalid_os_records_mapping.toDF()
            agency_invalid_os_records_df.write.option("truncate",True).jdbc(url=url, table="logs.qualagencyoserrors", mode=mode, properties=properties)
                                                            
        dyf = DynamicFrame.fromDF(agencypersonosdf_valid, glueContext, "dyf")
                                                                                                                                                                
        # Mapping of the filename columns to the target table coumns with its datatypes
        applymapping1 = ApplyMapping.apply(frame = dyf, mappings = [("Q_RecaptchaScore", "string", "q_recaptchascore", "string"), ("DistributionChannel", "string", "distributionchannel", "string"), ("Duration (in seconds)", "string", "duration_in_seconds", "string"),("RecipientFirstName", "string", "recipientfirstname", "string"), ("RecipientLastName", "string", "recipientlastname", "string"), ("ExternalReference", "string", "externalreference", "string"), ("RecipientEmail", "string", "recipientemail", "string"),("Q5_1", "string", "person_firstname", "string"), ("Q2_1", "string", "agency_firstname", "string"), ("Progress", "string", "progress", "string"), ("Status", "string", "status", "string"), ("EndDate", "string", "enddate", "string"), ("Q5_8", "string", "person_id", "string"),("filenamenew", "string", "filename", "string"),("filemodifieddate", "timestamp", "filemodifieddate", "timestamp"),("Q13", "string", "os_completion_date", "string"), ("ResponseId", "string", "responseid", "string"), ("Q5_3", "string", "person_dob", "string"), ("RecordedDate", "string", "recordeddate", "string"), ("Finished", "string", "finished", "string"), ("LocationLatitude", "string", "locationlatitude", "string"), ("LocationLongitude", "string", "locationlongitude", "string"), ("IPAddress", "string", "ipaddress", "string"), ("Q2_3", "string", "agency_email", "string"), ("StartDate", "string", "startdate", "string"), ("Q5_4", "string", "person_phone", "string"), ("UserLanguage", "string", "userlanguage", "string"), ("Q2_2", "string", "agency_lastname", "string"), ("Q5_2", "string", "person_lastname", "string"), ("Q4", "string", "employername", "string")], transformation_ctx = "applymapping1")
        
    
        selectfields2 = SelectFields.apply(frame = applymapping1, paths = ["ipaddress", "startdate", "userlanguage", "person_firstname", "agency_lastname", "person_lastname", "agency_email", "responseid", "person_id","recipientemail", "recipientfirstname", "externalreference", "recipientlastname", "agency_firstname","person_phone", "finished", "locationlongitude", "os_completion_date", "locationlatitude", "q_recaptchascore", "enddate", "distributionchannel", "person_dob", "employername", "progress", "recordeddate","filename", "status", "duration_in_seconds","filemodifieddate","filedate"], transformation_ctx = "selectfields2")
        
        resolvechoice3 = ResolveChoice.apply(frame = selectfields2, choice = "MATCH_CATALOG", database = catalog_database, table_name = catalog_table_prefix+"_raw_os_qual_agency_person", transformation_ctx = "resolvechoice3")
        resolvechoice4 = ResolveChoice.apply(frame = resolvechoice3, choice = "make_cols", transformation_ctx = "resolvechoice4")

        resolvechoice4.toDF().createOrReplaceTempView("agencypersonoscleandf")

        spark.sql("select * from agencypersonospreviousdf").show()
        spark.sql("select *,  true as isdelta from agencypersonoscleandf where trim(responseid) not in (select trim(responseid) from agencypersonospreviousdf)").show()
        spark.sql("select *, false as isdelta from agencypersonoscleandf where trim(responseid) in (select trim(responseid) from agencypersonospreviousdf)").show()

        
        # isDelta flag  is marked as true for new responseid not existing in data store and false for otherwise 
        agencypersonosdf_clean = spark.sql("""
        select *, true as isdelta from agencypersonoscleandf where trim(responseid) not in (select trim(responseid) from agencypersonospreviousdf)
            UNION 
        select *, false as isdelta from agencypersonoscleandf where trim(responseid) in (select trim(responseid) from agencypersonospreviousdf)
            """)

        agencypersonosdf_clean.show()
        agencypersonosdf_clean = agencypersonosdf_clean.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in agencypersonosdf_clean.columns])
        agencypersonosdf_clean.show()
        agencypersonosdf_clean.write.option("truncate",True).jdbc(url=url, table="raw.os_qual_agency_person", mode=mode, properties=properties)

        ## B2BDS-1385: insert an entry into the log
        # WRITE a record with process/execution time to logs.lastprocessed table
        lastprocessed_df = spark.createDataFrame(
            [('glue-qualtrics-os-completion-s3-to-raw', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])

        # Create Dynamic Frame to log lastprocessed table
        lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext,"lastprocessed_cdf")
        lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[("processname", "string", "processname", "string"), (
            "lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"), ("success", "string", "success", "string")])

        # Write to postgresql logs.lastprocessed table of the success
        glueContext.write_dynamic_frame.from_catalog(
            frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")
    else:
        print("File has already processed or no records in the file.")

    #Moving the processed file to archive location
    for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/qualtrics/O&SCompletion/"):
       if object_summary.key.endswith('csv'):
         filename = object_summary.key
         sourcekey = filename
         targetkey = sourcekey.replace("/raw/", "/archive/")
         copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
         s3bucket.copy(copy_source, targetkey)
         s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()
## B2BDS-1385: the else clause in case the files_list is empty
else:
    print("No file found in S3")
job.commit()