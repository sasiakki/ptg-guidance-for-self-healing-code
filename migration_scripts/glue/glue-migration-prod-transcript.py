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
transcript_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/training_history/transcript.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="transcript_gdf",
)

transcript_df = transcript_gdf.toDF()

transcript_df = transcript_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in transcript_df.columns
    ]
)

for colname in transcript_df.columns:
    transcript_df = transcript_df.withColumn(colname, trim(col(colname)))

transcript_cdf = DynamicFrame.fromDF(transcript_df, glueContext, "transcript_cdf")

# Script generated for node ApplyMapping
ApplyMapping_transcript = ApplyMapping.apply(
    frame=transcript_cdf,
    mappings=[
        ("personid", "string", "personid", "long"),
        ("transcriptid", "string", "transcriptid", "long"),
        ("coursename", "string", "coursename", "string"),
        ("courseid", "string", "courseid", "string"),
        ("completeddate", "string", "completeddate", "timestamp"),
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
        (
            "reasoncode",
            "string",
            "reasonfortransfer",
            "string",
        ),  # Changes as part of B2BDS-1343
    ],
    transformation_ctx="ApplyMapping_transcript",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_transcript,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_transcript",
)

job.commit()
