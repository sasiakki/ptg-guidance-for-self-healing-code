import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import DateType
from datetime import datetime
import boto3
import json
import pandas as pd
import csv

try:
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
    S3_BUCKET = s3_secrets['fileexchange']
    
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
    
    # Default JOB arguments
    args = getResolvedOptions(sys.argv, ["JOB_NAME"])
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args["JOB_NAME"], args)
    
    mode = "append"
    url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
    properties = {"user": B2B_USER, "password": B2B_PASSWORD,
                  "driver": "org.postgresql.Driver"}
    
    # Multiple files of the completions can be processed in same time
    sourcepath = "s3://"+S3_BUCKET+"/transcripts/creditretractions/"
    
    
    print("************Starting glue job execution**********************")
    
    rawnoshows = spark.read.format("csv").option("header","true").option("inferSchema","false").option("escape","\"").load(f"{sourcepath}")
    spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")
    rawnoshows = rawnoshows.withColumn("filename", input_file_name())
    rawnoshows = rawnoshows.withColumn("filenamenew",regexp_extract(col('filename'), '(s3://)(.*)(/transcripts/creditretractions/)(.*)', 4))
    rawnoshows = rawnoshows.withColumn("filedate",to_date(regexp_extract(col("filenamenew"),r'\d{2}\d{2}\d{2}',0),'MMddyy'))
    # Convert the column to the date type
    rawnoshows = rawnoshows.withColumn("completed", to_date(col("completed"), "dd-MM-yyyy").cast(DateType()))
    rawnoshows = rawnoshows.withColumn("archivedreason",lit("No Show"))
    
    #Removing the duplicates based on learner id and class id (course name) and marking eny blank values as nulls
    
    #Check if personid & transcript id have only digits and they are not nulls
    rawnoshows_valid = rawnoshows.filter(col("LEARNERID").isNotNull()).filter(col("TRANSCRIPTID").isNotNull()).filter(col("LEARNERID").rlike("""^[0-9]+$""")).filter(col("TRANSCRIPTID").rlike("""^[0-9]+$"""))
    #print("printing all valid records")
    #rawnoshows_valid.show(10)
    
    #Storing invalid records into another dataframe
    invalid_df=rawnoshows.withColumn("ErrorReason", when(~col("LEARNERID").rlike("^\d+$") | col("LEARNERID").isNull(),"Person ID is not valid").when(~col("TRANSCRIPTID").rlike("^\d+$") | col("TRANSCRIPTID").isNull(),"Transcript ID is not valid"))
    
    invalid_df=invalid_df.filter(col("ErrorReason").isNotNull())
    #print("printing all invalid records")
    #invalid_df.show()
    
    rawnoshows_catalog = DynamicFrame.fromDF(rawnoshows_valid, glueContext, "rawnoshows_catalog")
    
    # Apply Mapping for raw.transcriptretractions as target table
    rawnoshows_targetmapping = ApplyMapping.apply(
        frame=rawnoshows_catalog,
        mappings=[
            ("TRANSCRIPTID", "string", "Transcriptid", "long"),
            ("learnerid", "string", "personid", "long"),
            ("courseid", "string", "courseid", "string"),
            ("dshsid", "string", "dshsid", "string"),
            ("credits", "string", "credithours", "float"),
            ("completed", "date", "completeddate", "date"),
            ("Course Name", "string", "coursename", "string"),
            ("INSTRUCTORID", "string", "INSTRUCTORID", "string"),
            ("INSTRUCTOR", "string", "INSTRUCTOR", "string"),
            ("source", "string", "trainingsource", "string"),
            ("filenamenew","string","filename","string"),
            ("archivedreason","string","archivedreason","string")
        ],
        transformation_ctx="rawnoshows_targetmapping",
    )
    
    # Converting glue dynamic dataframe to spark dataframe
    rawnoshowsfinaldf = rawnoshows_targetmapping.toDF()
    
    # Appending the data to raw table
    rawnoshowsfinaldf.write.option("truncate", "false").jdbc(
        url=url, table="raw.transcriptretractions", mode=mode, properties=properties)
    
    #Saving Invalid records and exporting to S3 bucket
    if(invalid_df.count() > 0):
        print("Exporting and Saving invalid records to logs.noshowerrors")
            
        name_suffix = invalid_df.select("filenamenew").distinct().limit(1).collect()
        name_suffix = name_suffix[0].filenamenew
        print(name_suffix)
        invalid_df = invalid_df.drop("filename")
        invalid_df = invalid_df.withColumnRenamed("filenamenew","filename")
        #invalid_df.show(2,vertical=True)
        pandas_df = invalid_df.toPandas()
        print("Exporting to S3 bucket")
        # Export the invalid records to a S3 bucket
        pandas_df.to_csv("s3://"+ S3_BUCKET + "/transcripts/creditretractions/errors/s3_to_raw_error" + name_suffix, header=True, index=None,quotechar='"',encoding='utf-8', sep=',',quoting=csv.QUOTE_ALL)
        
        #Insert the invalid records in to logs.noshowerrors table
        newdatasource1 = DynamicFrame.fromDF(invalid_df, glueContext, "newdatasource1")
        applymapping1 = ApplyMapping.apply(frame = newdatasource1, mappings = [("TRANSCRIPTID", "string", "Transcriptid", "string"),
            ("learnerid", "string", "personid", "string"),
            ("courseid", "string", "courseid", "string"),
            ("dshsid", "string", "dshsid", "string"),
            ("credits", "string", "credithours", "float"),
            ("completed", "date", "completeddate", "string"),
            ("Course Name", "string", "coursename", "string"),
            ("INSTRUCTORID", "string", "INSTRUCTORID", "string"),
            ("INSTRUCTOR", "string", "INSTRUCTOR", "string"),
            ("source", "string", "trainingsource", "string"),
            ("filename","string","filename","string"),
            ("errorreason","string","errorreason","string"),
            ("archivedreason","string","archivedreason","string"),
            ("filedate", "date", "filedate", "date")], 
                transformation_ctx = "applymapping1")
        new_df1 = applymapping1.toDF()
        print("Inserting invalid records into logs table")
        mode = "append"
        new_df1.write.jdbc(url=url, table="logs.noshowerrors", mode=mode, properties=properties)    
    
    
    #Archiving Processed files
    #If we have Multiple files, then one file at time is moved to archive location
    for object_summary in s3bucket.objects.filter(Prefix="transcripts/creditretractions/"):
        if object_summary.key.endswith('csv') and "error" not in object_summary.key and "processed" not in object_summary.key:
            filename = object_summary.key
            sourcekey = filename
            print("source key is ",sourcekey)
            targetkey =  sourcekey.replace("/creditretractions/","/creditretractions/processed/")
            copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
            s3bucket.copy(copy_source, targetkey)
            s3resource.Object(""+S3_BUCKET+"", sourcekey).delete()

    ##insert an entry into the log
    # WRITE a record with process/execution time to logs.lastprocessed table
    lastprocessed_df = spark.createDataFrame(
        [('glue-transcript-noshow-s3-to-raw', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])

    # Create Dynamic Frame to log lastprocessed table
    lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext,"lastprocessed_cdf")
    lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[("processname", "string", "processname", "string"), (
        "lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"), ("success", "string", "success", "string")])

    # Write to postgresql logs.lastprocessed table of the success
    glueContext.write_dynamic_frame.from_catalog(
        frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")

    job.commit()
except Exception as e:
    print("Oops! Something unexpected occurred:", str(e))
print("************Completed glue job execution**********************")