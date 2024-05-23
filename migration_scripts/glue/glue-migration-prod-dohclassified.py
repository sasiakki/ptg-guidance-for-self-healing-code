import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, when, trim

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
classified_gdf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": True,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/doh_classified/dohclassified.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="classified_gdf",
)
classified_df = classified_gdf.toDF()
classified_df = classified_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in classified_df.columns
    ]
)

for colname in classified_df.columns:
    classified_df = classified_df.withColumn(colname, trim(col(colname)))

classified_cdf = DynamicFrame.fromDF(classified_df, glueContext, "classified_cdf")
# Script generated for node ApplyMapping
ApplyMapping_classified = ApplyMapping.apply(
    frame=classified_cdf,
    mappings=[
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("dohname", "string", "dohname", "string"),
        ("credentialstatus", "string", "credentialstatus", "string"),
        ("applicationdate", "string", "applicationdate", "date"),
        (
            "datedshsbenefitpaymentudfupdated",
            "string",
            "datedshsbenefitpaymentudfupdated",
            "date",
        ),
        ("classifieddate", "string", "classifieddate", "date"),
        ("appfeepaid", "string", "appfeepaid", "string"),
        ("reconciled", "string", "reconciled", "date"),
        ("reconnotes", "string", "reconnotes", "string"),
        ("filelastname", "string", "filelastname", "string"),
        ("filefirstname", "string", "filefirstname", "string"),
        ("filereceiveddate", "string", "filereceiveddate", "date"),
    ],
    transformation_ctx="ApplyMapping_classified",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_classified,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_dohclassified",
)

job.commit()
