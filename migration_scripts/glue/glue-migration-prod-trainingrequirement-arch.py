'''import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame

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
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/training_requirement/Arch_trainingrequirement/training_requirement_archived_20230215.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="S3bucket_node1",
)

df = S3bucket_node1.toDF()

df=df.select([when(col(c)=="",None).when(col(c)=="NULL",None).otherwise(col(c)).alias(c) for c in df.columns])
DataCatalogtable_node2 = DynamicFrame.fromDF(df, glueContext, "DataCatalogtable_node2")


# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=DataCatalogtable_node2,
    mappings=[
        ("trainingid", "string", "trainingid", "string"),
        ("is_archived", "string", "isarchived", "boolean"),
        ("archived_date", "string", "datearchived", "timestamp"),
        ("personid", "string", "personid", "bigint"),
        ("trackingdate", "string", "trackingdate", "timestamp"),
        ("requiredhours", "string", "requiredhours", "double"),
        ("earnedhours", "string", "earnedhours", "double"),
        ("transferredhours", "string", "transferredhours", "double"),
        ("duedate", "string", "duedate", "timestamp"),
        ("isoverride", "string", "isoverride", "boolean"),
        ("completeddate", "string", "completeddate", "timestamp"),
        ("status", "string", "status", "string"),
        ("isrequired", "string", "isrequired", "boolean"),
        ("duedateextension", "string", "duedateextension", "timestamp"),
        ("trainingprogram", "string", "trainingprogram", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("created", "string", "created", "timestamp"),
    ],
    transformation_ctx="ApplyMapping_node2",
)



# Script generated for node PostgreSQL table
PostgreSQLtable_node3 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_trainingrequirement_arch",
    transformation_ctx="PostgreSQLtable_node3",
)

job.commit()'''

