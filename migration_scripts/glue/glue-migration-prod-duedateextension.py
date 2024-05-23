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
duedateextension_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/prodduedateoverridehistory/duedateoverride_history.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="duedateextension_gdf",
)


duedateextension_df = duedateextension_gdf.toDF()
duedateextension_df = duedateextension_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in duedateextension_df.columns
    ]
)

for colname in duedateextension_df.columns:
    duedateextension_df = duedateextension_df.withColumn(colname, trim(col(colname)))

duedateextension_cdf = DynamicFrame.fromDF(
    duedateextension_df, glueContext, "duedateextension_cdf"
)

# Script generated for node ApplyMapping
ApplyMapping_duedateextension = ApplyMapping.apply(
    frame=duedateextension_cdf,
    mappings=[
        ("trainingid", "string", "trainingid", "string"),
        ("personid", "string", "personid", "long"),
        ("duedateoverride", "string", "duedateoverride", "timestamp"),
        ("duedateoverridereason", "string", "duedateoverridereason", "string"),
        ("bcapproveddate", "string", "bcapproveddate", "timestamp"),
    ],
    transformation_ctx="ApplyMapping_duedateextension",
)

# # Script generated for node PostgreSQL
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_duedateextension,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_duedateextension",
)

job.commit()
