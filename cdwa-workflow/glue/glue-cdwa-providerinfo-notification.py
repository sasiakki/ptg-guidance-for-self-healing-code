import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3
from botocore.exceptions import ClientError

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account["environment_type"]

if environment_type == "dev":
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"


# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ["JOB_NAME", "ProcessingType"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

print(args["ProcessingType"])
# Reading value from Input parmameter to the glue JOB
processing_type = args["ProcessingType"]


# datastore@myseiubenefits.org
SENDER = "datastore@myseiubenefits.org"
RECIPIENTS = ["datastore@myseiubenefits.org"]
# RECIPIENTS = ["datastore@myseiubenefits.org",
#              "CDWAIntegrationsteam@consumerdirectcare.com"]

# Multiple email addresses seprated with comma
# RECIPIENTS = ["email1@email.com","email2@email.com"]
# Insert email address if we need Carbon copy
# CCRECIPIENTS = [""]

# ConfigurationSetName=CONFIGURATION_SET argument below.
# CONFIGURATION_SET = "ConfigSet"
AWS_REGION = "us-west-2"
# The character encoding for the email.
CHARSET = "UTF-8"
SUBJECT = ""
BODY_TEXT = ""
BODY_HTML = ""

cdwa_raw_table = "_raw_cdwa"
# Script generated for node PostgreSQL table
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix + cdwa_raw_table,
    transformation_ctx="raw_cdwa",
).toDF().createOrReplaceTempView("raw_cdwa")

print("##########################################################")
print("Starting pipeline-p-cdwa-providerinfo-notification glue job")

# File processing notification message
if processing_type != "" and processing_type == "FileProcessing":
    print("File processing email message")

    latestfile = spark.sql(
        "SELECT filename, COUNT(*) as rows FROM raw_cdwa WHERE Cast(recordcreateddate as date) = CURRENT_DATE GROUP BY filename"
    )
    if latestfile.count() > 0:
        print(
            "File: {0} contains {1} no. of records.".format(
                latestfile.first()["filename"], latestfile.first()["rows"]
            )
        )
        # The subject line for the email.
        SUBJECT = "TP Datastore: {0} - Success".format(latestfile.first()["filename"])
        # print(SUBJECT)
        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = (
            "TP Datastore has received and processed the file: {0}\r\n"
            "Number of records: {1} \r\n"
            "Please feel free to contact us if any further information is required."
        ).format(latestfile.first()["filename"], latestfile.first()["rows"])
        # print(BODY_TEXT)
        # The HTML body of the email.
        BODY_HTML = """<html>
        <head></head>
        <body>
        <p>TP Datastore has received and processed the file: {0}.</p>
        <p>Number of records: {1}.</p>
        <p>Please feel free to contact us if any further information is required.</p>
        </body>
        </html>
        """.format(
            latestfile.first()["filename"], latestfile.first()["rows"]
        )
        # print(BODY_HTML)

# Data validation notification message
if processing_type != "" and processing_type == "DataValidation":
    print("Data validation email message")

    latestfile = spark.sql(
        "SELECT regexp_replace(filename,'.csv','-error.csv') as filename, COUNT(*) as rows FROM raw_cdwa WHERE isvalid = FALSE \
        AND Cast(recordcreateddate as date) = CURRENT_DATE GROUP BY filename"
    )
    if latestfile.count() > 0:
        print(
            "File: {0} contains {1} no. of error records.".format(
                latestfile.first()["filename"], latestfile.first()["rows"]
            )
        )
        # The subject line for the email.
        SUBJECT = "TP Datastore: {0} - Success".format(latestfile.first()["filename"])
        # print(SUBJECT)
        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = (
            "TP Datastore has uploaded the error file: {0} successfully to SFTP. \r\n"
            "Number of error records: {1} \r\n"
            "Please feel free to contact us if any further information is required."
        ).format(latestfile.first()["filename"], latestfile.first()["rows"])
        # print(BODY_TEXT)
        # The HTML body of the email.
        BODY_HTML = """<html>
        <head></head>
        <body>
        <p>TP Datastore has uploaded the error file: {0} successfully to SFTP.</p>
        <p>Number of error records: {1}.</p>
        <p>Please feel free to contact us if any further information is required.</p>
        </body>
        </html>
        """.format(
            latestfile.first()["filename"], latestfile.first()["rows"]
        )
        # print(BODY_HTML)

# Send email method
if (
    RECIPIENTS != ""
    and BODY_HTML != ""
    and processing_type != ""
    and latestfile.count() > 0
):
    print("Sending an email")

    # Create a new SES resource and specify a region.
    client = boto3.client("ses", region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": RECIPIENTS,
                # 'CcAddresses':CCRECIPIENTS,
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])
else:
    print("No new file processed today")

job.commit()

print("Completed pipeline-p-cdwa-providerinfo-notification glue job execution")
print("##########################################################")
