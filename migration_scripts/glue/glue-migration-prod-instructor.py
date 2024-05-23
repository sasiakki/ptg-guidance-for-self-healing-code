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
instructor_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/instructor/instructor.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="S3bucket_node1",
)

instructor_df = instructor_gdf.toDF()

instructor_df = instructor_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in instructor_df.columns
    ]
)
for colname in instructor_df.columns:
    instructor_df = instructor_df.withColumn(colname, trim(col(colname)))

instructor_cdf = DynamicFrame.fromDF(instructor_df, glueContext, "instructor_df")

# Script generated for node ApplyMapping
ApplyMapping_instructor = ApplyMapping.apply(
    frame=instructor_cdf,
    mappings=[
        ("instructorid", "string", "instructorid", "string"),
        ("firstname", "string", "firstname", "string"),
        ("lastname", "string", "lastname", "string"),
        ("dshsinstructorid", "string", "dshsinstructorid", "string"),
        ("email", "string", "email", "string"),
        ("isactive", "string", "isactive", "boolean"),
        (
            "trainingproviderexternalcode",
            "string",
            "trainingproviderexternalcode",
            "string",
        ),
    ],
    transformation_ctx="ApplyMapping_instructor",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_instructor,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_instructor",
)

job.commit()
