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
credential_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/credential/credential_delta.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="credential_gdf",
)

credential_df = credential_gdf.toDF()

credential_df = credential_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in credential_df.columns
    ]
)

for colname in credential_df.columns:
    credential_df = credential_df.withColumn(colname, trim(col(colname)))

credential_cdf = DynamicFrame.fromDF(credential_df, glueContext, "credential_cdf")


# Script generated for node ApplyMapping
ApplyMapping_credential = ApplyMapping.apply(
    frame=credential_cdf,
    mappings=[
        ("personid", "string", "personid", "long"),
        ("taxid", "string", "taxid", "int"),
        ("providernumber", "string", "providernumber", "long"),
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("providernamedshs", "string", "providernamedshs", "string"),
        ("providernamedoh", "string", "providernamedoh", "string"),
        ("dateofbirth", "string", "dateofbirth", "string"),
        (
            "limitedenglishproficiencyindicator",
            "string",
            "limitedenglishproficiencyindicator",
            "string",
        ),
        ("firstissuancedate", "string", "firstissuancedate", "string"),
        ("lastissuancedate", "string", "lastissuancedate", "string"),
        ("expirationdate", "string", "expirationdate", "string"),
        ("credentialtype", "string", "credentialtype", "string"),
        ("credentialstatus", "string", "credentialstatus", "string"),
        ("lepprovisionalcredential", "string", "lepprovisionalcredential", "string"),
        (
            "lepprovisionalcredentialissuedate",
            "string",
            "lepprovisionalcredentialissuedate",
            "string",
        ),
        (
            "lepprovisionalcredentialexpirationdate",
            "string",
            "lepprovisionalcredentialexpirationdate",
            "string",
        ),
        ("actiontaken", "string", "actiontaken", "string"),
        (
            "continuingeducationduedate",
            "string",
            "continuingeducationduedate",
            "string",
        ),
        ("longtermcareworkertype", "string", "longtermcareworkertype", "string"),
        (
            "excludedlongtermcareworker",
            "string",
            "excludedlongtermcareworker",
            "string",
        ),
        ("paymentdate", "string", "paymentdate", "string"),
        (
            "credentiallastdateofcontact",
            "string",
            "credentiallastdateofcontact",
            "string",
        ),
        ("preferredlanguage", "string", "preferredlanguage", "string"),
        ("credentialstatusdate", "string", "credentialstatusdate", "string"),
        ("nctrainingcompletedate", "string", "nctrainingcompletedate", "string"),
        ("examscheduleddate", "string", "examscheduleddate", "string"),
        ("examscheduledsitecode", "string", "examscheduledsitecode", "string"),
        ("examscheduledsitename", "string", "examscheduledsitename", "string"),
        ("examtestertype", "string", "examtestertype", "string"),
        ("examemailaddress", "string", "examemailaddress", "string"),
        ("examdtrecdschedtestdate", "string", "examdtrecdschedtestdate", "string"),
        ("phonenum", "string", "phonenum", "string"),
        ("hashidkey", "string", "hashidkey", "string"),
        ("primarycredential", "string", "primarycredential", "int"),
        ("modified", "string", "modified", "timestamp"),
        ("dateofhire", "string", "dateofhire", "string"),
        ("dohcertduedate", "string", "dohcertduedate", "date"),
        ("filename", "string", "filename", "string"),
        ("filemodifieddate", "string", "filemodifieddate", "timestamp"),
    ],
    transformation_ctx="ApplyMapping_credential",
)

# Script generated for node PostgreSQL table
glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_credential,
    database="seiubg-rds-b2bds",
    table_name="b2bds_raw_credential_delta",
)

job.commit()
