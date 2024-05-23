import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import input_file_name
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import (
    expr,
    col,
    regexp_replace,
    to_date,
    regexp_extract,
    when,
)
import boto3
import json

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON["environment_type"]

if environment_type == "dev":
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client("secretsmanager")


# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId=f"{environment_type}/b2bds/s3"
)
s3_secrets = json.loads(s3response["SecretString"])
S3_BUCKET = s3_secrets["datafeeds"]

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=f"{environment_type}/b2bds/rds/system-pipelines"
)
database_secrets = json.loads(databaseresponse["SecretString"])
B2B_USER = database_secrets["username"]
B2B_PASSWORD = database_secrets["password"]
B2B_HOST = database_secrets["host"]
B2B_PORT = database_secrets["port"]
B2B_DBNAME = database_secrets["dbname"]

mode = "overwrite"
url = "jdbc:postgresql://" + B2B_HOST + "/" + B2B_DBNAME
properties = {
    "user": B2B_USER,
    "password": B2B_PASSWORD,
    "driver": "org.postgresql.Driver",
}

# Reading files from s3 and sorting it by last modified date to read only the earliest file

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

s3 = boto3.resource("s3")
bucket = s3.Bucket(S3_BUCKET)

checkpath = "Case Manager IP Transition Report w Demographics"
objects = list(bucket.objects.filter(Prefix="Inbound/raw/cdwa/transition/"))
for i in objects:
    if checkpath in str(i):
        objects.sort(key=lambda o: o.last_modified)
        print(objects[0].key)

        # Script generated for node Data Catalog table
        DataCatalogtable_node1 = glueContext.create_dynamic_frame.from_options(
            format_options={
                "quoteChar": '"',
                "withHeader": True,
                "separator": ",",
                "inferSchema": False,
            },
            connection_type="s3",
            format="csv",
            connection_options={
                "paths": ["s3://" + S3_BUCKET + "/" + objects[0].key + ""],
                "recurse": True,
            },
            transformation_ctx="DataCatalogtable_node1",
        )
        cdwatransition_df = DataCatalogtable_node1.toDF().withColumn(
            "filename", input_file_name()
        )
        cdwatransition_df = cdwatransition_df.withColumn(
            "filename",
            regexp_replace(
                "filename", "s3://" + S3_BUCKET + "/Inbound/raw/cdwa/transition/", ""
            ),
        )
        cdwatransition_df = cdwatransition_df.withColumn(
            "filedate",
            to_date(
                regexp_extract(
                    col("filename"),
                    "(Case Manager IP Transition Report w Demographics )(\d\d\d\d\d\d\d\d)(.csv)",
                    2,
                ),
                "MMddyyyy",
            ),
        )
        cdwatransition_df = cdwatransition_df.withColumn("ssn", expr("RIGHT(ssn, 4)"))
        cdwatransition_df = cdwatransition_df.select(
            [
                when(col(c) == "", None).otherwise(col(c)).alias(c)
                for c in cdwatransition_df.columns
            ]
        )
        cdwatransition_df.show(truncate=False)
        cdwatransition_df.printSchema()

        DataCatalogtable_node2 = DynamicFrame.fromDF(
            cdwatransition_df, glueContext, "DataCatalogtable_node2"
        )

        # Script generated for node ApplyMapping
        ApplyMapping_node2 = ApplyMapping.apply(
            frame=DataCatalogtable_node2,
            mappings=[
                ("providerone ipid", "string", "providerone_id", "string"),
                ("workday id", "string", "workdayid", "string"),
                ("person id", "string", "personid", "string"),
                ("category", "string", "category", "string"),
                ("sub category", "string", "subcategory", "string"),
                ("status", "string", "status", "string"),
                ("ssn", "string", "ssn", "string"),
                ("hire date", "string", "hiredate", "string"),
                ("birth date", "string", "birthdate", "string"),
                ("ip name", "string", "ipname", "string"),
                ("firstname", "string", "firstname", "string"),
                ("middlename", "string", "middlename", "long"),
                ("lastname", "string", "lastname", "long"),
                ("email", "string", "email", "string"),
                ("home phone", "string", "homephone", "string"),
                ("cell phone", "string", "cellphone", "string"),
                ("address type", "string", "addresstype", "string"),
                ("address line 1", "string", "addressline1", "string"),
                ("address line 2", "string", "addressline2", "string"),
                ("city", "string", "city", "string"),
                ("state", "string", "state", "string"),
                ("zip code", "string", "zipcode", "string"),
                ("preferred language", "string", "preferredlanguage", "string"),
                (
                    "recommended preferred language",
                    "string",
                    "recommendedpreferredlanguage",
                    "string",
                ),
                ("filename", "string", "filename", "string"),
                ("filedate", "date", "filedate", "timestamp"),
            ],
            transformation_ctx="ApplyMapping_node2",
        )

        # ##########################Overwrite script - start ####################################

        final_df = ApplyMapping_node2.toDF()

        final_df.write.option("truncate", True).jdbc(
            url=url, table="raw.cdwatransitionreports", mode=mode, properties=properties
        )

        sourcekey = objects[0].key
        targetkey = objects[0].key.replace("/raw/", "/archive/")
        print(sourcekey)
        print(targetkey)
        copy_source = {"Bucket": S3_BUCKET, "Key": sourcekey}
        bucket.copy(copy_source, targetkey)
        s3.Object(S3_BUCKET, sourcekey).delete()

        print("completed writing")

    # ##########################Overwrite script - end ####################################
    else:
        print("no files")


print("done")


job.commit()
