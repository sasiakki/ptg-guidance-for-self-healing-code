'''import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/transcript_transfer/transcript_transfer.csv"
        ]
    },
    transformation_ctx="S3bucket_node1",
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=S3bucket_node1,
    mappings=[
        ("transferid", "string", "transferid", "bigint"),
        ("personid", "string", "personid", "bigint"),
        ("coursename", "string", "classname", "string"),
        ("courseid", "string", "courseid", "string"),
        ("completeddate", "string", "completeddate", "date"),
        ("credithours", "string", "transferhours", "double"),
        ("trainingprogram", "string", "trainingprogram", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("dshscourseid", "string", "dshscoursecode", "string"),
        ("trainingsource", "string", "transfersource", "string"),
        ("trainingid", "string", "trainingid", "string"),
        ("reasoncode", "string", "reasonfortransfer", "string"),
    ],
    transformation_ctx="ApplyMapping_node2",
)

# Script generated for node PostgreSQL table
PostgreSQLtable_node3 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_trainingtransfers",
    transformation_ctx="PostgreSQLtable_node3",
)

job.commit()
'''
