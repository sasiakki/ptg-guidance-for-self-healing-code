import boto3
from datetime import datetime
import csv
import boto3
import json
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col
from awsglue.utils import getResolvedOptions

# @params: [JOB_NAME]
today = datetime.now()
suffix = today.strftime("%m_%d_%Y")
print(suffix)

# environment_type
args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account["environment_type"]

if environment_type == "prod":
    bg_learning_s3_bucket_name = "seiu-learning-center"
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"
elif environment_type == "stage":
    bg_learning_s3_bucket_name = "stage-seiu-learning-center"
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"
else:
    bg_learning_s3_bucket_name = "bg-learning-center"
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client("secretsmanager")


# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId="{0}/b2bds/s3".format(environment_type)
)
s3_secrets = json.loads(s3response["SecretString"])
S3_BUCKET = s3_secrets["datafeeds"]


def main():
    sc = SparkContext()
    glueContext = GlueContext(sc)

    outboundDF = glueContext.create_data_frame.from_catalog(
        database=catalog_database,
        table_name=catalog_table_prefix + "_staging_personquarantine",
        transformation_ctx="outboundDF",
    )

    outboundDF.printSchema()
    outboundDF = (
        outboundDF.withColumn("hiredate", col("hiredate").cast("String"))
        .withColumn("trackingdate", col("trackingdate").cast("String"))
        .withColumn("person_unique_id", col("person_unique_id").cast("String"))
        .withColumn("cdwaid", col("cdwaid").cast("String"))
        .withColumn("dshsid", col("dshsid").cast("String"))
        .withColumn("personid", col("personid").cast("String"))
    )
    outboundDF.printSchema()
    pandas_df = outboundDF.toPandas()
    # print(pandas_df.dtypes)
    pandas_df.to_csv(
        "s3://"
        + bg_learning_s3_bucket_name
        + "/quarantine/inbound/Quarantined-Persons-"
        + suffix
        + ".csv",
        header=True,
        index=None,
        sep=",",
        encoding="utf-8-sig",
        quoting=csv.QUOTE_ALL,
    )
    pandas_df.to_csv(
        "s3://"
        + S3_BUCKET
        + "/Outbound/PersonQuarantine/Quarantined-Persons-"
        + suffix
        + ".csv",
        header=True,
        index=None,
        sep=",",
        encoding="utf-8-sig",
        quoting=csv.QUOTE_ALL,
    )


if __name__ == "__main__":
    main()
