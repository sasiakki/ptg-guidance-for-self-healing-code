import sys
from awsglue.transforms import ApplyMapping
from pyspark.sql.functions import when, trim, col
from awsglue.dynamicframe import DynamicFrame
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
person_gdf = glueContext.create_dynamic_frame.from_options(
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
            "s3://seiubg-b2bds-prod-data-migration-m2y7e/exports/person/person.csv"
        ],
        "recurse": True,
    },
    transformation_ctx="person_gdf",
)

person_df = person_gdf.toDF()

person_df = person_df.select(
    [
        when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c)
        for c in person_df.columns
    ]
)

for colname in person_df.columns:
    person_df = person_df.withColumn(colname, trim(col(colname)))

person_df.show()
person_df.printSchema()

person_dyf = DynamicFrame.fromDF(person_df, glueContext, "DataCatalogtable_node2")


# Script generated for node ApplyMapping
persondyf_applymapping = ApplyMapping.apply(
    frame=person_dyf,
    mappings=[
        ("personid", "string", "personid", "long"),
        ("sfcontactid", "string", "sfcontactid", "string"),
        ("firstname", "string", "firstname", "string"),
        ("middlename", "string", "middlename", "string"),
        ("lastname", "string", "lastname", "string"),
        ("ssn", "string", "ssn", "string"),
        ("dob", "string", "dob", "string"),
        ("email1", "string", "email1", "string"),
        ("email2", "string", "email2", "string"),
        ("homephone", "string", "homephone", "string"),
        ("trainingstatus", "string", "trainingstatus", "string"),
        ("mobilephone", "string", "mobilephone", "string"),
        ("language", "string", "language", "string"),
        ("physicaladdress", "string", "physicaladdress", "string"),
        ("mailingaddress", "string", "mailingaddress", "string"),
        ("mailingstreet1", "string", "mailingstreet1", "string"),
        ("mailingstreet2", "string", "mailingstreet2", "string"),
        ("mailingcity", "string", "mailingcity", "string"),
        ("mailingstate", "string", "mailingstate", "string"),
        ("mailingzip", "string", "mailingzip", "string"),
        ("mailingcountry", "string", "mailingcountry", "string"),
        ("dshsid", "string", "dshsid", "long"),
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("cdwaid", "string", "cdwaid", "long"),
        ("matched_sourcekeys", "string", "matched_sourcekeys", "string"),
        ("status", "string", "status", "string"),
        ("exempt", "string", "exempt", "string"),
        ("hiredate", "string", "hiredate", "timestamp"),
        ("type", "string", "type", "string"),
        ("workercategory", "string", "workercategory", "string"),
        ("categorycode", "string", "categorycode", "string"),
        ("trackingdate", "string", "trackingdate", "date"),
        ("iscarinaeligible", "string", "iscarinaeligible", "boolean"),
        ("ahcas_eligible", "string", "ahcas_eligible", "boolean"),
        ("lasttermdate", "string", "lasttermdate", "date"),
        ("rehiredate", "string", "rehiredate", "date"),
    ],
    transformation_ctx="persondyf_applymapping",
)


glueContext.write_dynamic_frame.from_catalog(
    frame=persondyf_applymapping,
    database="seiubg-rds-b2bds",
    table_name="b2bds_prod_person",
)

job.commit()
