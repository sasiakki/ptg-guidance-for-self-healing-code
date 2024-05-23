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
traineestatuslogs_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/traineestatuslogs/traineestatuslogs.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="traineestatuslogs_gdf",
)


traineestatuslogs_df = traineestatuslogs_gdf.toDF()

traineestatuslogs_df = traineestatuslogs_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in traineestatuslogs_df.columns
    ]
)

for colname in traineestatuslogs_df.columns:
    traineestatuslogs_df = traineestatuslogs_df.withColumn(colname, trim(col(colname)))

traineestatuslogs_dyf = DynamicFrame.fromDF(
    traineestatuslogs_df, glueContext, "traineestatuslogs_dyf"
)

# Script generated for node ApplyMapping
traineestatuslogs_mapping = ApplyMapping.apply(
    frame=traineestatuslogs_dyf,
    mappings=[
        ("employeeid", "string", "employeeid", "string"),
        ("personid", "string", "personid", "long"),
        ("compliancestatus", "string", "compliancestatus", "string"),
        ("trainingexempt", "string", "trainingexempt", "string"),
        ("trainingprogram", "string", "trainingprogram", "string"),
        ("trainingstatus", "string", "trainingstatus", "string"),
        ("classname", "string", "classname", "string"),
        ("dshscoursecode", "string", "dshscoursecode", "string"),
        ("credithours", "string", "credithours", "decimal"),
        ("completeddate", "string", "completeddate", "string"),
        ("filename", "string", "filename", "string"),
    ],
    transformation_ctx="traineestatuslogs_mapping",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=traineestatuslogs_mapping,
    database="seiubg-rds-b2bds",
    table_name="b2bds_logs_traineestatuslogs",
)

job.commit()
