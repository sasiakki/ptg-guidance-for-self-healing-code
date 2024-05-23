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
personhistory_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/personhistory/staging_personhistory.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="personhistory_gdf",
)

personhistory_df = personhistory_gdf.toDF()

personhistory_df = personhistory_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in personhistory_df.columns
    ]
)
for colname in personhistory_df.columns:
    personhistory_df = personhistory_df.withColumn(colname, trim(col(colname)))

personhistory_cdf = DynamicFrame.fromDF(
    personhistory_df, glueContext, "personhistory_df"
)

# Script generated for node ApplyMapping
ApplyMapping_personhistory = ApplyMapping.apply(
    frame=personhistory_cdf,
    mappings=[
        ("personid", "string", "personid", "long"),
        ("firstname", "string", "firstname", "string"),
        ("lastname", "string", "lastname", "string"),
        ("ssn", "string", "ssn", "string"),
        ("email1", "string", "email1", "string"),
        ("mobilephone", "string", "mobilephone", "string"),
        ("language", "string", "language", "string"),
        ("physicaladdress", "string", "physicaladdress", "string"),
        ("mailingaddress", "string", "mailingaddress", "string"),
        ("status", "string", "status", "string"),
        ("exempt", "string", "exempt", "string"),
        ("hiredate", "string", "hiredate", "timestamp"),
        ("type", "string", "type", "string"),
        ("workercategory", "string", "workercategory", "string"),
        ("categorycode", "string", "categorycode", "string"),
        ("modified", "string", "modified", "timestamp"),
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("sourcekey", "string", "sourcekey", "string"),
        ("dshsid", "string", "dshsid", "long"),
        ("dob", "string", "dob", "string"),
        ("cdwa_id", "string", "cdwa_id", "int"),
        ("email2", "string", "email2", "string"),
        ("homephone", "string", "homephone", "string"),
        ("trackingdate", "string", "trackingdate", "timestamp"),
        ("iscarinaeligible", "string", "iscarinaeligible", "boolean"),
        ("trainingstatus", "string", "trainingstatus", "string"),
        ("middlename", "string", "middlename", "string"),
        ("mailingstreet1", "string", "mailingstreet1", "string"),
        ("mailingstreet2", "string", "mailingstreet2", "string"),
        ("mailingcity", "string", "mailingcity", "string"),
        ("mailingstate", "string", "mailingstate", "string"),
        ("mailingzip", "string", "mailingzip", "string"),
        ("mailingcountry", "string", "mailingcountry", "string"),
        ("filemodifieddate", "string", "filemodifieddate", "date"),
        ("preferred_language", "string", "preferred_language", "string"),
        (
            "ip_contract_expiration_date",
            "string",
            "ip_contract_expiration_date",
            "date",
        ),
        ("agencyid", "string", "agencyid", "long"),
        ("last_background_check_date", "string", "last_background_check_date", "date"),
        ("ie_date", "string", "ie_date", "date"),
        ("ahcas_eligible", "string", "ahcas_eligible", "boolean"),
    ],
    transformation_ctx="ApplyMapping_personhistory",
)


# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_personhistory,
    database="seiubg-rds-b2bds",
    table_name="b2bds_staging_personhistory",
)

job.commit()
