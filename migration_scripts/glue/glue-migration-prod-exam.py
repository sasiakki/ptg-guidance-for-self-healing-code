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
exam_gdf = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": True,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/exam/exam.csv"],
        "recurse": True,
    },
    transformation_ctx="S3bucket_node1",
)

exam_df = exam_gdf.toDF()

exam_df = exam_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in exam_df.columns
    ]
)
for colname in exam_df.columns:
    exam_df = exam_df.withColumn(colname, trim(col(colname)))

exam_cdf = DynamicFrame.fromDF(exam_df, glueContext, "exam_cdf")

# Script generated for node ApplyMapping
ApplyMapping_exam = ApplyMapping.apply(
    frame=exam_cdf,
    mappings=[
        ("studentid", "string", "studentid", "string"),
        ("taxid", "string", "taxid", "string"),
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("examdate", "string", "examdate", "string"),
        ("examstatus", "string", "examstatus", "string"),
        ("examtitlefromprometrics", "string", "examtitlefromprometrics", "string"),
        ("testlanguage", "string", "testlanguage", "string"),
        ("testsite", "string", "testsite", "string"),
        ("sitename", "string", "sitename", "string"),
        (
            "rolesandresponsibilitiesofthehomecareaide",
            "string",
            "rolesandresponsibilitiesofthehomecareaide",
            "string",
        ),
        (
            "supportingphysicalandpsychosocialwellbeing",
            "string",
            "supportingphysicalandpsychosocialwellbeing",
            "string",
        ),
        ("promotingsafety", "string", "promotingsafety", "string"),
        ("handwashingskillresult", "string", "handwashingskillresult", "string"),
        ("randomskill1result", "string", "randomskill1result", "string"),
        ("randomskill2result", "string", "randomskill2result", "string"),
        ("randomskill3result", "string", "randomskill3result", "string"),
        (
            "commoncarepracticesskillresult",
            "string",
            "commoncarepracticesskillresult",
            "string",
        ),
        # ("filemodifieddate", "string", "filemodifieddate", "timestamp"),
        # ("filename", "string", "filename", "string"),
    ],
    transformation_ctx="ApplyMapping_exam",
)

# Script generated for node Drop Null Fields

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_exam,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_exam",
)

job.commit()
