import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import input_file_name, regexp_extract, col, to_timestamp, when
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
import boto3
import json
import re
from datetime import datetime
from heapq import nsmallest

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
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
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

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
s3bucket = s3resource.Bucket(S3_BUCKET)

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,
              "driver": "org.postgresql.Driver"}
# s3://seiubg-b2bds-prod-feeds-fp7mk/Inbound/raw/exam/01250_TPExam_ADSAToTP_20220411_055213.TXT

print("************Starting glue job execution**********************")

files_list = {}
for object_summary in s3bucket.objects.filter(Prefix="Inbound/raw/exam/"):
    if object_summary.key.endswith('TXT'):
        filename = object_summary.key
        filedate = datetime.strptime(re.search(
            r"(Inbound/raw/exam/)(01250_TPExam_ADSAToTP_)(\d\d\d\d\d\d\d\d_\d\d\d\d\d\d)(.TXT)", object_summary.key).group(3), '%Y%m%d_%H%M%S').date()
        files_list[filename] = filedate

# Creating the md5 for comparision to the previous day's data and registering it to a Temp view
exampreviousdf = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=catalog_table_prefix+"_raw_exam", transformation_ctx="exampreviousdf")

exampreviousdf.toDF().selectExpr("md5(concat_ws('',studentid, taxid, credentialnumber, examdate, examstatus,examtitlefromprometrics, testlanguage, testsite, sitename, rolesandresponsibilitiesofthehomecareaide,supportingphysicalandpsychosocialwellbeing,promotingsafety, handwashingskillresult,randomskill2result,randomskill3result,commoncarepracticesskillresult)) as examhashid").createOrReplaceTempView("exampreviousdf")

if len(files_list) != 0:

    # N Smallest values in dictionary (N=1)(Values are dates and capturing the smallest date) Using nsmallest
    processingfilekey = nsmallest(1, files_list, key=files_list.get).pop()
    sourcepath = "s3://"+S3_BUCKET+"/"+processingfilekey+""

    # Read data from S3 Bucket
    examdf = glueContext.create_dynamic_frame.from_options(
        format_options={"withHeader": True,
                        "separator": "|", "optimizePerformance": True},
        connection_type="s3",
        format="csv",
        connection_options={
            "paths": [sourcepath],
            "recurse": True,
        },
        transformation_ctx="S3bucket_node1",
    ).toDF()

    examdf = examdf.withColumn("inputfilename", input_file_name())
    examdf = examdf.withColumn("filename", regexp_extract(
        col('inputfilename'), '(s3://)(.*)(/Inbound/raw/exam/)(.*)', 4))
    examdf = examdf.withColumn("filemodifieddate", to_timestamp(regexp_extract(col(
        'filename'), '(01250_TPExam_ADSAToTP_)(\d\d\d\d\d\d\d\d_\d\d\d\d\d\d)(.TXT)', 2), "yyyyMMdd_HHmmss"))
    examdf = examdf.select([when(col(c) == "", None).otherwise(
        col(c)).alias(c) for c in examdf.columns])

    # ApplyMapping to match the target table
    exam_raw_node = DynamicFrame.fromDF(examdf, glueContext, "exam_raw_node")
    applymapping_exam_raw = ApplyMapping.apply(
        frame=exam_raw_node,
        mappings=[
            ("studentid", "string", "studentid", "string"),
            ("taxid", "string", "taxid", "string"),
            ("filename", "string", "filename", "string"),
            ("filemodifieddate", "timestamp", "filemodifieddate", "timestamp"),
            ("credentialnumber", "string", "credentialnumber", "string"),
            ("examdate", "string", "examdate", "string"),
            ("examstatus", "string", "examstatus", "string"),
            ("examtitlefromprometrics", "string",
             "examtitlefromprometrics", "string"),
            ("testlanguage", "string", "testlanguage", "string"),
            ("testsite", "string", "testsite", "string"),
            ("sitename", "string", "sitename", "string"),
            ("rolesandresponsibilitiesofthehomecareaide", "string",
             "rolesandresponsibilitiesofthehomecareaide", "string"),
            ("supportingphysicalandpsychosocialwellbeing", "string",
             "supportingphysicalandpsychosocialwellbeing", "string"),
            ("promotingsafety", "string", "promotingsafety", "string"),
            ("handwashingskillresult", "string",
             "handwashingskillresult", "string"),
            ("randomskill1result", "string", "randomskill1result", "string"),
            ("randomskill2result", "string", "randomskill2result", "string"),
            ("randomskill3result", "string", "randomskill3result", "string"),
            ("commoncarepracticesskillresult", "string",
             "commoncarepracticesskillresult", "string"),
        ],
        transformation_ctx="applymapping_exam_raw",
    )
    examdf_clean = applymapping_exam_raw.toDF()
    examdf_clean.createOrReplaceTempView("examcleandf")

    # Creating the md5 for comparision
    examdf_clean = spark.sql(""" select *, md5(concat_ws('',studentid, taxid, credentialnumber, examdate, examstatus,examtitlefromprometrics, testlanguage, testsite, sitename, rolesandresponsibilitiesofthehomecareaide,supportingphysicalandpsychosocialwellbeing,promotingsafety, handwashingskillresult,randomskill2result,randomskill3result,commoncarepracticesskillresult)) as examhashid from examcleandf """)
    examdf_clean.createOrReplaceTempView("examcleandf")

    # Capturing the delta if record is not previously processed with hash value
    trueDelta = spark.sql(
        """select *, true as isdelta from examcleandf where trim(examhashid) not in (select trim(examhashid) from exampreviousdf)""")
    trueDelta.show()
    falseDelta = spark.sql(
        """select *, false as isdelta from examcleandf where trim(examhashid) in (select trim(examhashid) from exampreviousdf)""")
    falseDelta.show()
    examdf_clean = spark.sql("""
    select *, true as isdelta from examcleandf where trim(examhashid) not in (select trim(examhashid) from exampreviousdf)
        UNION 
    select *, false as isdelta from examcleandf where trim(examhashid) in (select trim(examhashid) from exampreviousdf)
        """).drop("examhashid")

    # Truncating and loading the processed data
    examdf_clean.write.option("truncate", True).jdbc(
        url=url, table="raw.exam", mode=mode, properties=properties)

    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {'Bucket': S3_BUCKET, 'Key': sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(S3_BUCKET, sourcekey).delete()

print("************Completed glue job execution**********************")
job.commit()
