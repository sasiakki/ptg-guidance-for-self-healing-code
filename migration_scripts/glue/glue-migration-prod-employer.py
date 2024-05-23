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
employer_gdf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": True,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/employer/employer.csv"],
        "recurse": True,
    },
    transformation_ctx="employer_gdf",
)


employer_df = employer_gdf.toDF()
employer_df = employer_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in employer_df.columns
    ]
)

for colname in employer_df.columns:
    employer_df = employer_df.withColumn(colname, trim(col(colname)))

employer_cdf = DynamicFrame.fromDF(
    employer_df, glueContext, "employer_cdf"
)

# Script generated for node ApplyMapping
ApplyMapping_employer = ApplyMapping.apply(
    frame=employer_cdf,
    mappings=[
        ("employerid", "string", "employerid", "int"),
        ("employername", "string", "employername", "string"),
        ("type", "string", "type", "string"),
        ("address", "string", "address", "string"),
    ],
    transformation_ctx="ApplyMapping_employer",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_employer,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_employer",
)

job.commit()
