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
employertrust_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/employer_trust/employertrust.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="employertrust_gdf",
)

employertrust_df = employertrust_gdf.toDF()
employertrust_df = employertrust_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in employertrust_df.columns
    ]
)

for colname in employertrust_df.columns:
    employertrust_df = employertrust_df.withColumn(colname, trim(col(colname)))

employertrust_cdf = DynamicFrame.fromDF(
    employertrust_df, glueContext, "employertrust_cdf"
)


# Script generated for node ApplyMapping
ApplyMapping_employertrust = ApplyMapping.apply(
    frame=employertrust_cdf,
    mappings=[
        ("trustid", "string", "trustid", "int"),
        ("employerid", "string", "employerid", "int"),
        ("name", "string", "name", "string"),
        ("type", "string", "type", "string"),
        ("trust", "string", "trust", "string"),
        ("sourcename", "string", "sourcename", "string"),
        ("startdate", "string", "startdate", "string"),
        ("enddate", "string", "enddate", "string"),
    ],
    transformation_ctx="ApplyMapping_employertrust",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_employertrust,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_employertrust",
)

job.commit()
