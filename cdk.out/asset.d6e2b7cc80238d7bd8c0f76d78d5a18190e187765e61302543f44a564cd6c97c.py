import boto3
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
import sys
import json
import csv
from awsglue.transforms import ApplyMapping
from awsglue.dynamicframe import DynamicFrame

args_environment = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_environment["environment_type"]

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

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
    SecretId=f"{environment_type}/b2bds/s3"
)
s3_secrets = json.loads(s3response["SecretString"])
S3_BUCKET = s3_secrets["datafeeds"]


def main():
    outbound_vw_cdwa_errorfile = glueContext.create_dynamic_frame.from_catalog(
        database=catalog_database,
        table_name=f"{catalog_table_prefix}_outbound_vw_cdwa_errorfile",
        transformation_ctx="outbound_vw_cdwa_errorfile",
    ).toDF()

    filemodifieddate = outbound_vw_cdwa_errorfile.first()["filemodifieddate"]

    filename = f"CDWA-O-BG-ProviderInfo-{filemodifieddate}-error.csv"

    pandas_df = outbound_vw_cdwa_errorfile.toPandas()

    pandas_df.to_csv(
        f"s3://{S3_BUCKET}/Outbound/cdwa/providerinfo_errorlog/{filename}",
        header=True,
        index=None,
        quotechar='"',
        encoding="utf-8",
        sep=",",
        quoting=csv.QUOTE_ALL,
    )
    
     # WRITE a record with process/execution time to logs.lastprocessed table
    lastprocessed_df = spark.createDataFrame(
            [("glue-cdwa-error-to-s3", filemodifieddate, "1")],
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
            table_name=f"{catalog_table_prefix}_logs_lastprocessed",
        )


if __name__ == "__main__":
    main()
