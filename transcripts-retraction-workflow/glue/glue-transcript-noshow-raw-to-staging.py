import sys
from awsglue.transforms import SelectFields, ApplyMapping, ResolveChoice, DropNullFields
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col,udf,lit
from awsglue.dynamicframe import DynamicFrame
from datetime import datetime
from pyspark.sql.types import DateType
import boto3
import json
import pandas as pd
import re
import csv

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')
    
# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(SecretId=environment_type+'/b2bds/s3')
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['fileexchange']

s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

# Define a UDF (User-Defined Function) to extract the date from the filename
def extract_file_date(filename):
    # Extract the date from the filename using appropriate logic
    # Modify the logic based on the actual filename format
    #samplenoshow06262023.csv   
    file_date = re.search(r"(.*)(\d\d\d\d\d\d\d\d)(.csv)", filename).group(2)
    # Convert the extracted date string to a DateType
    file_date = datetime.strptime(file_date, "%m%d%Y").date()
    return file_date

# Register the UDF
extract_file_date_udf = udf(extract_file_date, DateType())


# Create the Glue Catalog Temp Table for transcriptretractions and LastProcessed Tables

# read data from raw.transcriptretractions table
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=catalog_table_prefix+"_raw_transcriptretractions")\
        .toDF().createOrReplaceTempView("transcriptretractions")

# read data from logs.lastprocessed table
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")\
    .toDF().createOrReplaceTempView("lastprocessed")

# read data from prod.person table
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_prod_person")\
    .toDF().select("personid").createOrReplaceTempView("prodperson")
    
# read data from prod.transcript table
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_prod_transcript")\
    .toDF().select("personid","transcriptid").createOrReplaceTempView("prodtranscript")



# Delta Detection

spark.sql(""" 
    SELECT ID,
	TRANSCRIPTID,
	PERSONID,
	COURSEID,
	DSHSID,
	CREDITHOURS,
	COMPLETEDDATE,
	COURSENAME,
	INSTRUCTORID,
	INSTRUCTOR,
	TRAININGSOURCE,
	FILENAME,
	ARCHIVEDREASON
FROM TRANSCRIPTRETRACTIONS
WHERE RECORDMODIFIEDDATE >
		(SELECT CASE
					WHEN MAX(LASTPROCESSEDDATE) IS NULL THEN (CURRENT_DATE-1)
					ELSE MAX(LASTPROCESSEDDATE)
				END AS MAXPROCESSDATE
			FROM LASTPROCESSED L
			WHERE PROCESSNAME = 'glue-noshow-raw-to-staging'
				AND SUCCESS = '1')
                    """).createOrReplaceTempView("rawtranscripretractions")
                    
	


# Error Records Identification
    
spark.sql(""" 
SELECT A.ID,
	A.TRANSCRIPTID,
	A.PERSONID,
	A.COURSEID,
	A.DSHSID,
	A.CREDITHOURS,
	A.COMPLETEDDATE,
	A.COURSENAME,
	A.INSTRUCTORID,
	A.INSTRUCTOR,
	A.TRAININGSOURCE,
	A.REASON,
	A.FILENAME,
	A.ARCHIVEDREASON
FROM
	(SELECT A.ID,
			A.TRANSCRIPTID,
			A.PERSONID,
			A.COURSEID,
			A.DSHSID,
			A.CREDITHOURS,
			A.COMPLETEDDATE,
			A.COURSENAME,
			A.INSTRUCTORID,
			A.INSTRUCTOR,
			A.TRAININGSOURCE,
			CASE
				WHEN C.TRANSCRIPTID IS NULL THEN 'TranscriptID Does Not Exist'
                WHEN B.PERSONID IS NULL THEN 'PersonID Does Not Exist'
				WHEN D.TRANSCRIPTID IS NULL THEN 'TranscriptID does not belong to the PersonID'
			END AS REASON,
			A.FILENAME,
			A.ARCHIVEDREASON
		FROM RAWTRANSCRIPRETRACTIONS A
		LEFT JOIN PRODPERSON B ON A.PERSONID = B.PERSONID
		LEFT JOIN PRODTRANSCRIPT C ON A.TRANSCRIPTID = C.TRANSCRIPTID
        LEFT JOIN PRODTRANSCRIPT D ON A.PERSONID = D.PERSONID
		AND A.TRANSCRIPTID = D.TRANSCRIPTID) A
WHERE A.REASON IS NOT NULL""").createOrReplaceTempView("invalid_transcripretractions")
	


# Valid Records 

valid_transcripretractionsdf = spark.sql(""" 
SELECT A.ID,
	A.TRANSCRIPTID,
	A.PERSONID,
	A.COURSEID,
	A.DSHSID,
	A.CREDITHOURS,
	A.COMPLETEDDATE,
	A.COURSENAME,
	A.INSTRUCTORID,
	A.INSTRUCTOR,
	A.TRAININGSOURCE,
	A.FILENAME,
	A.ARCHIVEDREASON
FROM RAWTRANSCRIPRETRACTIONS A
LEFT JOIN INVALID_TRANSCRIPRETRACTIONS B ON A.ID = B.ID
WHERE B.ID IS NULL
	               """)

valid_transcripretractionsdf = valid_transcripretractionsdf.withColumn("filedate", extract_file_date_udf(col("filename")))

common_cols=valid_transcripretractionsdf.columns


## WRITE to staging.transcriptretractions table

rawtranscriptretractionsdatasource = DynamicFrame.fromDF(
    valid_transcripretractionsdf, glueContext, "rawtranscriptretractionsdatasource")
transcripretractionsapplymapping = ApplyMapping.apply(frame=rawtranscriptretractionsdatasource, mappings=[
    ("id", "long", "id", "long"),
    ("transcriptid", "long", "transcriptid", "long"),
    ("personid", "long", "personid", "long"),
    ("courseid", "string", "courseid", "string"),
    ("dshsid", "string", "dshsid", "string"),
    ("credithours", "decimal", "credithours", "decimal"),
    ("completeddate", "date", "completeddate", "date"),
    ("coursename", "string", "coursename", "string"),
    ("instructorid", "string", "instructorid", "string"),
    ("instructor", "string", "instructor", "string"),
    ("trainingsource", "string", "trainingsource", "string"),
    ("filename", "string", "filename", "string"),
    ("archivedreason", "string", "archivedreason", "string"),
    ("filedate", "date", "filedate", "date"),
])


stagingtranscriptretractions = SelectFields.apply(frame=transcripretractionsapplymapping,
                                                  paths=["id", "transcriptid", "personid", "courseid",
                                                         "dshsid", "credithours",
                                                         "completeddate", "coursename", "instructorid",
                                                         "instructor", "trainingsource", "filename", "filedate",
                                                         "archivedreason"])

stagingtranscriptretractionsmapping = ResolveChoice.apply(frame=stagingtranscriptretractions,
                                                          choice="MATCH_CATALOG",
                                                          database=catalog_database,
                                                          table_name=f"{catalog_table_prefix}_staging_transcriptretractions")

noshowdropnulls = DropNullFields.apply(
    frame=stagingtranscriptretractionsmapping)

glueContext.write_dynamic_frame.from_catalog(frame=noshowdropnulls, database=catalog_database,
                                             table_name=f"{catalog_table_prefix}_staging_transcriptretractions")



## WRITE to logs.transcriptretractionerrors table

invalid_transcripretractionsdf = spark.table("invalid_transcripretractions")

invalid_transcripretractionsdf = invalid_transcripretractionsdf.withColumn("filedate", extract_file_date_udf(col("filename")))

invalid_transcripretractionsdf = invalid_transcripretractionsdf.withColumn("recordcreateddate",lit(datetime.now())).withColumn("recordmodifieddate ",lit(datetime.now()))

invalid_rawtranscriptretractionsdatasource = DynamicFrame.fromDF(
    invalid_transcripretractionsdf, glueContext, "invalid_rawtranscriptretractionsdatasource")
invalid_transcripretractionsapplymapping = ApplyMapping.apply(frame=invalid_rawtranscriptretractionsdatasource, mappings=[
    ("id", "long", "id", "long"),
    ("transcriptid", "long", "transcriptid", "long"),
    ("personid", "long", "personid", "long"),
    ("courseid", "string", "courseid", "string"),
    ("dshsid", "string", "dshsid", "string"),
    ("credithours", "decimal", "credithours", "decimal"),
    ("completeddate", "date", "completeddate", "date"),
    ("coursename", "string", "coursename", "string"),
    ("instructorid", "string", "instructorid", "string"),
    ("instructor", "string", "instructor", "string"),
    ("trainingsource", "string", "trainingsource", "string"),
    ("reason", "string", "errorreason", "string"),
    ("filename", "string", "filename", "string"),
    ("archivedreason", "string", "archivedreason", "string"),
    ("filedate", "date", "filedate", "date"),
    ("recordcreateddate", "date", "recordcreateddate", "date"),
    ("recordmodifieddate ", "date", "recordmodifieddate ", "date"),
])


invalid_stagingtranscriptretractions = SelectFields.apply(frame=invalid_transcripretractionsapplymapping,
                                                  paths=["id", "transcriptid", "personid", "courseid",
                                                         "dshsid", "credithours",
                                                         "completeddate", "coursename", "instructorid",
                                                         "instructor", "trainingsource", "errorreason", "filename", "filedate",
                                                         "archivedreason", "recordcreateddate", "recordmodifieddate"])

invalid_stagingtranscriptretractionsmapping = ResolveChoice.apply(frame=invalid_stagingtranscriptretractions,
                                                          choice="MATCH_CATALOG",
                                                          database=catalog_database,
                                                          table_name=f"{catalog_table_prefix}_logs_transcriptretractionerrors")

invalid_noshowdropnulls = DropNullFields.apply(
    frame=invalid_stagingtranscriptretractionsmapping)

glueContext.write_dynamic_frame.from_catalog(frame=invalid_noshowdropnulls, database=catalog_database,
                                             table_name=f"{catalog_table_prefix}_logs_transcriptretractionerrors")



# Unload logs to s3


if(invalid_noshowdropnulls.count() > 0):
    suffix = str(datetime.now().strftime("%Y-%m-%d"))
    pandas_df = invalid_noshowdropnulls.toDF().toPandas()
    filename = pandas_df["filename"][0]
    extractname = filename[:-12]
    pandas_df.to_csv("s3://"+S3_BUCKET+"/transcripts/creditretractions/errors/"+extractname+suffix +"_errors.csv", header = True, index = None, quotechar= '"', encoding ='utf-8', sep =',',quoting = csv.QUOTE_ALL)
    print(suffix)
    print ("Invalid records: {0}".format(invalid_noshowdropnulls.count()))
                    



# WRITE a record with process/execution time to logs.lastprocessed table
lastprocessed_df = spark.createDataFrame(
    [('glue-noshow-raw-to-staging', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])

# Create Dynamic Frame to log lastprocessed table
lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext,"lastprocessed_cdf")

lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[("processname", "string", "processname", "string"), (
    "lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"), ("success", "string", "success", "string")])

# Write to postgresql logs.lastprocessed table of the success
glueContext.write_dynamic_frame.from_catalog(
    frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")

job.commit()
