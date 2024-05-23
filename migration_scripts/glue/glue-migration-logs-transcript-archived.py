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
transcript_archive_cdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/transcript_archive/transcript_archive.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="transcript_archive_cdf",
)

transcript_archive_df = transcript_archive_cdf.toDF()

transcript_archive_df = transcript_archive_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in transcript_archive_df.columns
    ]
)

for colname in transcript_archive_df.columns:
    transcript_archive_df = transcript_archive_df.withColumn(colname, trim(col(colname)))

transcript_archive_dyf = DynamicFrame.fromDF(
    transcript_archive_df, glueContext, "transcript_archive_dyf"
)

# Script generated for node ApplyMapping
transcript_archive_dyf_mapping = ApplyMapping.apply(
    frame=transcript_archive_dyf,
    mappings=[
        ("personid", "string", "personid", "long"),
        ("transcriptid", "string", "transcriptid", "long"),
        ("coursename", "string", "coursename", "string"),
        ("courseid", "string", "courseid", "string"),
        ("completeddate", "string", "completeddate", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("instructorid", "string", "instructorid", "string"),
        ("credithours", "string", "credithours", "double"),
        ("coursetype", "string", "coursetype", "string"),
        ("trainingprogram", "string", "trainingprogram", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("dshscourseid", "string", "dshscourseid", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
        ("trainingid", "string", "trainingid", "string"),
        ("learningpath", "string", "learningpath", "string"),
        ("reasoncode", "string", "reasonfortransfer", "string"),
        ("archived", "string", "archived", "timestamp"),
        (
            "reasonforarchival",
            "string",
            "reasonforarchival",
            "string",
        ),  # Changes as part of B2BDS-1343
    ],
    transformation_ctx="transcript_archive_dyf_mapping",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=transcript_archive_dyf_mapping,
    database="seiubg-rds-b2bds",
    table_name="b2bds_logs_transcriptarchived",
)

job.commit()
