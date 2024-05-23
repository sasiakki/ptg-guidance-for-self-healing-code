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
trainingrequirement_gdf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        #"optimizePerformance": True,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": [
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/training_requirement/training_requirement.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="trainingrequirement_gdf",
)

trainingrequirement_df = trainingrequirement_gdf.toDF()

trainingrequirement_df = trainingrequirement_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in trainingrequirement_df.columns
    ]
)

for colname in trainingrequirement_df.columns:
    trainingrequirement_df = trainingrequirement_df.withColumn(colname, trim(col(colname)))

trainingrequirement_df.printSchema()
trainingrequirement_df.show(1,truncate=False,vertical=True)

trainingrequirement_cdf = DynamicFrame.fromDF(
    trainingrequirement_df, glueContext, "trainingrequirement_cdf"
)


# Script generated for node ApplyMapping
ApplyMapping_trainingrequirement = ApplyMapping.apply(
    frame=trainingrequirement_cdf,
    mappings=[
        ("trainingid", "string", "trainingid", "string"),
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
        ("duedateoverridereason", "string", "duedateoverridereason", "string"),
        ("learningpath", "string", "learningpath", "string"),
        (
            "totalhours",
            "string",
            "totalhours",
            "double"
        ),  # Changes as part of B2BDS-1343
        ("archived", "string", "archived", "timestamp"),
    ],
    transformation_ctx="ApplyMapping_trainingrequirement",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_trainingrequirement,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_trainingrequirement",
)

job.commit()
