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
employmentrelationship_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/prodemploymentrelationship/prodemploymentrelationship.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="employmentrelationship_gdf",
)

employmentrelationship_df = employmentrelationship_gdf.toDF()

employmentrelationship_df = employmentrelationship_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in employmentrelationship_df.columns
    ]
)

for colname in employmentrelationship_df.columns:
    employmentrelationship_df = employmentrelationship_df.withColumn(
        colname, trim(col(colname))
    )

employmentrelationship_cdf = DynamicFrame.fromDF(
    employmentrelationship_df, glueContext, "employmentrelationship_cdf"
)

# Script generated for node ApplyMapping
ApplyMapping_employmentrelationship = ApplyMapping.apply(
    frame=employmentrelationship_cdf,
    mappings=[
        ("relationshipid", "string", "relationshipid", "long"),
        ("personid", "string", "personid", "long"),
        ("employeeid", "string", "employeeid", "long"),
        ("employerid", "string", "employerid", "string"),
        ("branchid", "string", "branchid", "int"),
        ("workercategory", "string", "workercategory", "string"),
        ("categorycode", "string", "categorycode", "string"),
        ("hiredate", "string", "hiredate", "timestamp"),
        ("authstart", "string", "authstart", "string"),
        ("authend", "string", "authend", "string"),
        ("empstatus", "string", "empstatus", "string"),
        ("terminationdate", "string", "terminationdate", "string"),
        ("trackingdate", "string", "trackingdate", "string"),
        ("isoverride", "string", "isoverride", "boolean"),
        ("isignored", "string", "isignored", "boolean"),
        ("sfngrecordid", "string", "sfngrecordid", "string"),
        ("source", "string", "source", "string"),
        ("role", "string", "role", "string"),
        ("createdby", "string", "createdby", "string"),
        ("relationship", "string", "relationship", "string"),
        ("filedate", "string", "filedate", "date"),
        ("priority", "string", "priority", "int"),
        ("agencyid", "string", "agencyid", "bigint"),
        ("rehiredate", "string", "rehiredate", "date"),
    ],
    transformation_ctx="ApplyMapping_employmentrelationship",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_employmentrelationship,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_employmentrelationship",
)

job.commit()
