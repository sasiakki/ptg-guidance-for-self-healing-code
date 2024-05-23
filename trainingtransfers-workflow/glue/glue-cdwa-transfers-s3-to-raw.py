import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import to_date, when, regexp_extract, col, input_file_name
import boto3
import json


# Default JOB arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)


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
    SecretId=environment_type+'/b2bds/s3'	
)	
s3_secrets = json.loads(s3response['SecretString'])	
S3_BUCKET = s3_secrets['datafeeds']


# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource("s3")
s3bucket = s3resource.Bucket(S3_BUCKET)


# Multiple files of the tranfers can be processed in same time
sourcepath = "s3://" + S3_BUCKET + "/Inbound/raw/cdwa/trainingtransfer/"


# Script for S3 bucket to read file in format CDWA-O-BG-TrainingTrans-_XX.csv
cdwatransfersdf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "inferSchema": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [sourcepath],
        "recurse": True,
    },
).toDF()
cdwatransfersdf.show()

if cdwatransfersdf.count() != 0:
    # Access the lastprocessed log table and create a DF for Delta Detection purpose
    
    logslastprocesseddf = glueContext.create_dynamic_frame.from_catalog(
        database=catalog_database,
        table_name=catalog_table_prefix + "_logs_lastprocessed",
        transformation_ctx="logsdf",
    )

    logslastprocesseddf = logslastprocesseddf.toDF().createOrReplaceTempView(
        "logslastprocessed"
    )

    # Capturing the processing file name, date
    cdwatransfersdf = (
        cdwatransfersdf.withColumn("inputfilename", input_file_name())
        .withColumn(
            "filename",
            regexp_extract(
                col("inputfilename"),
                "(s3://)(.*)(/Inbound/raw/cdwa/trainingtransfer/)(.*)",
                4,
            ),
        )
        .withColumn(
            "filemodifieddate",
            to_date(
                regexp_extract(
                    col("filename"),
                    "(CDWA-O-BG-TrainingTrans-)(\d\d\d\d-\d\d-\d\d)(.csv)",
                    2,
                ),
                "yyyy-MM-dd",
            ),
        )
    )
    # Insert into raw table only if new file has filemodifieddate > lastprocesseddate from the log table
    cdwatransfersdf.createOrReplaceTempView("cdwatransfersdata")
    cdwatransfersdf = spark.sql(
        """SELECT * FROM cdwatransfersdata WHERE filemodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                  END AS MAXPROCESSDATE FROM logslastprocessed WHERE processname='glue-cdwa-transfers-s3-to-raw' AND success='1')"""
    )

    # Only proceed if new files are detected. If the file already existed (filedate <= last processed date), then archive the file with a message "Data has already processed or no new data from the source table."
    if cdwatransfersdf.count() > 0:
        #maxfiledate = spark.sql("""select max(filemodifieddate) as filemodifieddate  from cdwatransfersdata """).first()["filemodifieddate"]
        maxfiledate = cdwatransfersdf.selectExpr("max(filemodifieddate) as max_date").first()["max_date"]
        
        # marking empty columns as null's
        cdwatransfersdf = cdwatransfersdf.select(
            [
                when(col(c) == "", None).otherwise(col(c)).alias(c)
                for c in cdwatransfersdf.columns
            ]
        )

        # Converting columns into appropriate type posible and renaming
        cdwatransfersdf = (
            cdwatransfersdf.withColumn(
                "completed_date", to_date(col("Completed Date"), "yyyyMMdd")
            )
            .withColumn("created_date", to_date(col("CreatedDate"), "yyyyMMdd"))
            .withColumnRenamed("Person ID", "personid")
        )
        cdwatransfersdf.show(1)
        cdwatransfers_datacatalog = DynamicFrame.fromDF(
            cdwatransfersdf, glueContext, "cdwatransfers_datacatalog"
        )
        transfers_mapping = ApplyMapping.apply(
            frame=cdwatransfers_datacatalog,
            mappings=[
                ("employee id", "string", "employeeid", "bigint"),
                ("personid", "string", "personid", "bigint"),
                ("training program", "string", "trainingprogram", "string"),
                ("class name", "string", "classname", "string"),
                ("dshs course code", "string", "dshscoursecode", "string"),
                ("credit hours", "string", "credithours", "string"),
                ("completed_date", "date", "completeddate", "date"),
                ("training entity", "string", "trainingentity", "string"),
                ("reason for transfer", "string", "reasonfortransfer", "string"),
                ("employerstaff", "string", "employerstaff", "string"),
                ("created_date", "date", "createddate", "date"),
                ("filename", "string", "filename", "string"),
                ("filemodifieddate", "date", "filedate", "date"),
            ],
            transformation_ctx="transfers_mapping",
        )

        # Appending all cdwa training transfers cdwatrainingtransfers
        glueContext.write_dynamic_frame.from_catalog(
            frame=transfers_mapping,
            database=catalog_database,
            table_name=catalog_table_prefix + "_raw_cdwatrainingtransfers",
        )

        # WRITE a record with process/execution time to logs.lastprocessed table
        lastprocessed_df = spark.createDataFrame(
            [("glue-cdwa-transfers-s3-to-raw", maxfiledate, "1")],
            schema=["processname", "lastprocesseddate", "success"],
        )

        # Create Dynamic Frame to log lastprocessed table
        lastprocessed_cdf = DynamicFrame.fromDF(
            lastprocessed_df, glueContext, "lastprocessed_cdf"
        )
        lastprocessed_cdf_applymapping = ApplyMapping.apply(
            frame=lastprocessed_cdf,
            mappings=[
                ("processname", "string", "processname", "string"),
                ("lastprocesseddate", "date", "lastprocesseddate", "timestamp"),
                ("success", "string", "success", "string"),
            ],
        )

        # Write to postgresql logs.lastprocessed table of the success
        glueContext.write_dynamic_frame.from_catalog(
            frame=lastprocessed_cdf_applymapping,
            database=catalog_database,
            table_name=catalog_table_prefix + "_logs_lastprocessed",
        )

    else:
        print("File has already processed or no records in the file.")
else:
    print("No csv files found in S3 bucket")

# Archiving Processed files
# If we have Multiple files of the tranfers, then one file at time is moved to archive location
for object_summary in s3bucket.objects.filter(
    Prefix="Inbound/raw/cdwa/trainingtransfer/"
):
    if object_summary.key.endswith("csv"):
        filename = object_summary.key
        sourcekey = filename
        targetkey = sourcekey.replace("/raw/", "/archive/")
        copy_source = {"Bucket": S3_BUCKET, "Key": sourcekey}
        s3bucket.copy(copy_source, targetkey)
        s3resource.Object(S3_BUCKET, sourcekey).delete()

job.commit()
