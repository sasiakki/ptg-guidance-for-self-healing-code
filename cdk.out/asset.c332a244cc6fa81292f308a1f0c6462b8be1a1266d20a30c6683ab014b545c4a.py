import boto3
from datetime import datetime
import pandas
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import first, lit, col
from awsglue.transforms import *
import csv
import json
from awsglue.utils import getResolvedOptions
import sys

# suffix
today = datetime.now()
suffix = today.strftime("%Y-%m-%d")
filename = "CDWA-I-BG-TrainingStatusUpdate-" + suffix + ".csv"
print(suffix)

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON["environment_type"]

if environment_type == "dev":
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client("secretsmanager")
# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId=environment_type + "/b2bds/s3"
)
s3_secrets = json.loads(s3response["SecretString"])
S3_BUCKET = s3_secrets["datafeeds"]
s3resource = boto3.resource("s3")
s3bucket = s3resource.Bucket("" + S3_BUCKET + "")


def main():
    sc = SparkContext()
    glueContext = GlueContext(sc)

    dyf = glueContext.create_dynamic_frame.from_catalog(
        database=catalog_database,
        table_name=catalog_table_prefix + "_outbound_cdwa_trainingstatus",
        transformation_ctx="dyf",
    )

    outboundDF = dyf.toDF()
    outboundDF = outboundDF.withColumn("Employee ID", col("employee id").cast("String"))
    pandas_df = outboundDF.toPandas()
    pandas_df.to_csv(
        "s3://" + S3_BUCKET + "/Outbound/cdwa/Trainee_status_file/" + filename,
        index=None,
        sep=",",
        mode="w",
        encoding="utf-8",
        quoting=csv.QUOTE_ALL,
    )

    outboudlogdf = outboundDF.withColumn("filename", lit(filename))
    outboudlogdf = DynamicFrame.fromDF(outboudlogdf, glueContext, "outboudlogdf")

    # Script generated for node ApplyMapping
    ApplyMapping_node2 = ApplyMapping.apply(
        frame=outboudlogdf,
        mappings=[
            ("employee id", "string", "employeeid", "string"),
            ("person id", "long", "personid", "long"),
            ("compliance status", "string", "compliancestatus", "string"),
            ("training exempt", "string", "trainingexempt", "string"),
            ("training program", "string", "trainingprogram", "string"),
            ("training program status", "string", "trainingstatus", "string"),
            ("class name", "string", "classname", "string"),
            ("dshs course code", "string", "dshscoursecode", "string"),
            ("credit hours", "decimal", "credithours", "decimal"),
            ("completed date", "string", "completeddate", "date"),
            ("filename", "string", "filename", "string"),
        ],
        transformation_ctx="ApplyMapping_node2",
    )

    # Script generated for node PostgreSQL table
    glueContext.write_dynamic_frame.from_catalog(
        frame=ApplyMapping_node2,
        database=catalog_database,
        table_name=catalog_table_prefix + "_logs_traineestatuslogs",
    )


if __name__ == "__main__":
    main()
