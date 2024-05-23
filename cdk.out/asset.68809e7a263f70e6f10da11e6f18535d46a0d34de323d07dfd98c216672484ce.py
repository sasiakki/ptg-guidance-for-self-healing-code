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
coursecatalog_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/course_catalog/coursecatalog.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="coursecatalog_gdf",
)

coursecatalog_df = coursecatalog_gdf.toDF()

coursecatalog_df = coursecatalog_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in coursecatalog_df.columns
    ]
)

for colname in coursecatalog_df.columns:
    coursecatalog_df = coursecatalog_df.withColumn(colname, trim(col(colname)))

coursecatalog_dyf = DynamicFrame.fromDF(coursecatalog_df, glueContext, "branch_dyf")


# Script generated for node ApplyMapping
ApplyMapping_coursecatalog = ApplyMapping.apply(
    frame=coursecatalog_dyf,
    mappings=[
        ("courseid", "string", "courseid", "string"),
        ("coursename", "string", "coursename", "string"),
        ("coursetype", "string", "coursetype", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("credithours", "string", "credithours", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("courseversion", "string", "courseversion", "string"),
        ("status", "string", "status", "string"),
        # ("enddate", "string", "enddate", "string"),
        ("dshscourseid", "string", "dshscourseid", "string"),
    ],
    transformation_ctx="ApplyMapping_coursecatalog",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_coursecatalog,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_coursecatalog",
)

job.commit()
