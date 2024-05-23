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
completed_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/doh_completed/dohcompleted.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="completed_gdf",
)
completed_df = completed_gdf.toDF()
completed_df = completed_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in completed_df.columns
    ]
)

for colname in completed_df.columns:
    completed_df = completed_df.withColumn(colname, trim(col(colname)))

completed_cdf = DynamicFrame.fromDF(completed_df, glueContext, "completed_cdf")
# Script generated for node ApplyMapping
ApplyMapping_completed = ApplyMapping.apply(
    frame=completed_cdf,
    mappings=[
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("dohname", "string", "dohname", "string"),
        ("credentialstatus", "string", "credentialstatus", "string"),
        ("applicationdate", "string", "applicationdate", "date"),
        ("dateinstructorupdated", "string", "dateinstructorupdated", "date"),
        ("approvedinstructorcode", "string", "approvedinstructorcode", "string"),
        ("approvedinstructorname", "string", "approvedinstructorname", "string"),
        ("dategraduatedfor70hours", "string", "dategraduatedfor70hours", "date"),
        ("completeddate", "string", "completeddate", "date"),
        ("examfeepaid", "string", "examfeepaid", "string"),
        ("reconciled", "string", "reconciled", "date"),
        ("reconnotes", "string", "reconnotes", "string"),
        ("filelastname", "string", "filelastname", "string"),
        ("filefirstname", "string", "filefirstname", "string"),
        ("filereceiveddate", "string", "filereceiveddate", "date"),
    ],
    transformation_ctx="ApplyMapping_completed",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_completed,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_dohcompleted",
)

job.commit()
