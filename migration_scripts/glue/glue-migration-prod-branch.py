import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import when, trim, col
from awsglue.dynamicframe import DynamicFrame

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
branch_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/branch/branch.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="branch_cdf",
)

branch_df = branch_gdf.toDF()

branch_df = branch_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in branch_df.columns
    ]
)

for colname in branch_df.columns:
    branch_df = branch_df.withColumn(colname, trim(col(colname)))

branch_dyf = DynamicFrame.fromDF(branch_df, glueContext, "branch_dyf")


# Script generated for node ApplyMapping
ApplyMapping_branch_dyf = ApplyMapping.apply(
    frame=branch_dyf,
    mappings=[
        ("branchid", "string", "branchid", "int"),
        ("branchname", "string", "branchname", "string"),
        ("branchcode", "string", "branchcode", "string"),
        ("address", "string", "address", "string"),
        ("employerid", "string", "employerid", "string"),
        ("phone", "string", "phone", "string"),
    ],
    transformation_ctx="ApplyMapping_branch_dyf",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_branch_dyf,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_branch",
)

job.commit()
