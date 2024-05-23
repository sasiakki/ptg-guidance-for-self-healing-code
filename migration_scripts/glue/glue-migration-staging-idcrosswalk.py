import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from cryptography.fernet import Fernet
from awsglue.dynamicframe import DynamicFrame
import boto3
import json
from pyspark.sql.functions import *

# Get fernet key from secretsmanager
secretsmanager_client = boto3.client("secretsmanager")
fernet_response = secretsmanager_client.get_secret_value(
    SecretId="prod/b2bds/glue/fernet"
)
fernet_secret = json.loads(fernet_response["SecretString"])
fernet_key = fernet_secret["key"]


# Define Encrypt User Defined Function
def encrypt_val(clear_text, MASTER_KEY):
    f = Fernet(MASTER_KEY)
    clear_text_b = bytes(clear_text, "utf-8")
    cipher_text = f.encrypt(clear_text_b)
    cipher_text = str(cipher_text.decode("ascii"))
    return cipher_text


# Register UDF's
encrypt = udf(encrypt_val, StringType())

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
idcrosswalk_gdf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/idcrosswalk/idcrosswalk.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="idcrosswalk_gdf",
)

idcrosswalk_df = idcrosswalk_gdf.toDF()

idcrosswalk_df = idcrosswalk_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in idcrosswalk_df.columns
    ]
)

for colname in idcrosswalk_df.columns:
    idcrosswalk_df = idcrosswalk_df.withColumn(colname, trim(col(colname)))

idcrosswalk_df = idcrosswalk_df.withColumn("fullssn", encrypt("ssn", lit(fernet_key)))

idcrosswalk_cdf = DynamicFrame.fromDF(idcrosswalk_df, glueContext, "idcrosswalk_cdf")


# Script generated for node ApplyMapping
ApplyMapping_idcrosswalk = ApplyMapping.apply(
    frame=idcrosswalk_cdf,
    mappings=[
        ("personid", "string", "personid", "long"),
        ("fullssn", "string", "fullssn", "string"),
        ("sfngid", "string", "sfngid", "string"),
        ("cdwaid", "string", "cdwaid", "long"),
        ("dshsid", "string", "dshsid", "long"),
    ],
    transformation_ctx="ApplyMapping_idcrosswalk",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_idcrosswalk,
    database="seiubg-rds-b2bds",
    table_name="b2bds_staging_idcrosswalk",
)

job.commit()
