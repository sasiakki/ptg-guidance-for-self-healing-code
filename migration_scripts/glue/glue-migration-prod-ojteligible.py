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
ojteligible_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/OJTEligible/ojteligible.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="ojteligible_gdf",
)

ojteligible_df = ojteligible_gdf.toDF()

ojteligible_df = ojteligible_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in ojteligible_df.columns
    ]
)
for colname in ojteligible_df.columns:
    ojteligible_df = ojteligible_df.withColumn(colname, trim(col(colname)))

ojteligible_cdf = DynamicFrame.fromDF(ojteligible_df, glueContext, "ojteligible_df")

# Script generated for node ApplyMapping
ApplyMapping_ojteligible = ApplyMapping.apply(
    frame=ojteligible_cdf,
    mappings=[
        ("personid", "string", "personid", "bigint"),
        ("appliedhours", "string", "appliedhours", "double"),
        ("pendinghours", "string", "pendinghours", "double"),
    ],
    transformation_ctx="ApplyMapping_ojteligible",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_ojteligible,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_ojteligible",
)

job.commit()
