import sys
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import (
    input_file_name,
    to_date,
    regexp_extract,
    substring,
    format_string,
    upper,
    col,
    lit,
    when,
    udf,
)
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import StringType
from cryptography.fernet import Fernet
import boto3
import json
import re
from datetime import datetime
from heapq import nsmallest


args_environment = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_environment["environment_type"]

if environment_type == "dev":
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"

# Initialize SparkContext and GlueContext
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Accessing the Secrets Manager from boto3 lib
secretsmanagerclient = boto3.client("secretsmanager")

# Accessing the secrets value for S3 Bucket
s3response = secretsmanagerclient.get_secret_value(
    SecretId=environment_type + "/b2bds/s3"
)
s3_secrets = json.loads(s3response["SecretString"])
S3_BUCKET = s3_secrets["datafeeds"]

# Accessing the secrets target database
databaseresponse = secretsmanagerclient.get_secret_value(
    SecretId=environment_type + "/b2bds/rds/system-pipelines"
)

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource("s3")
s3bucket = s3resource.Bucket(S3_BUCKET)


fernet_response = secretsmanagerclient.get_secret_value(
    SecretId=environment_type + "/b2bds/glue/fernet"
)
fernet_secrets = json.loads(fernet_response["SecretString"])
fernet_key = fernet_secrets["key"]

database_secrets = json.loads(databaseresponse["SecretString"])
B2B_USER = database_secrets["username"]
B2B_PASSWORD = database_secrets["password"]
B2B_HOST = database_secrets["host"]
B2B_PORT = database_secrets["port"]
B2B_DBNAME = database_secrets["dbname"]

mode = "overwrite"
url = f"jdbc:postgresql://{B2B_HOST}:{B2B_PORT}/{B2B_DBNAME}"
properties = {
    "user": B2B_USER,
    "password": B2B_PASSWORD,
    "driver": "org.postgresql.Driver",
}


# Define Encrypt User Defined Function
def encrypt_val(clear_text, MASTER_KEY):
    # if clear_text:
    f = Fernet(MASTER_KEY)
    clear_text_b = bytes(clear_text, "utf-8")
    cipher_text = f.encrypt(clear_text_b)
    cipher_text = str(cipher_text.decode("ascii"))
    return cipher_text


# Define Decrypt User Defined Function
def decrypt_val(cipher_text, MASTER_KEY):
    from cryptography.fernet import Fernet

    f = Fernet(MASTER_KEY)
    clear_val = f.decrypt(cipher_text.encode()).decode()
    return clear_val


# Register UDFs for encryption and decryption of the SSN based on the Fernet key
encrypt = udf(encrypt_val, StringType())
decrypt = udf(decrypt_val, StringType())

files_list = {}
for fileobj in s3bucket.objects.filter(Prefix="Inbound/raw/cdwa/ProviderInfo/"):
    if fileobj.key.endswith("csv"):
        filename = fileobj.key
        filedate = datetime.strptime(
            re.search(
                r"(Inbound/raw/cdwa/ProviderInfo/)(CDWA-O-BG-ProviderInfo-)(\d\d\d\d-\d\d-\d\d)(.csv)",
                fileobj.key,
            ).group(3),
            "%Y-%m-%d",
        ).date()
        files_list[filename] = filedate

if len(files_list) != 0:
    glueContext.create_dynamic_frame.from_catalog(
        database=catalog_database,
        table_name=catalog_table_prefix + "_logs_lastprocessed",
    ).toDF().createOrReplaceTempView("vwlogslastprocessed")

    processingfilekey = nsmallest(1, files_list, key=files_list.get).pop()

    sourcepath = f"s3://{S3_BUCKET}/{processingfilekey}"

    rawcdwa_cdf = (
        spark.read.format("csv")
        .option("header", "true")
        .option("quote", '"')
        .option("escape", '"')
        .option("charset", "utf-8")
        .load(sourcepath)
    )

    rawcdwadf = (
        rawcdwa_cdf.select(
            [
                when(col(c) == "", None)
                .when(col(c) == "NULL", None)
                .otherwise(col(c))
                .alias(c)
                for c in rawcdwa_cdf.columns
            ]
        )
        .withColumn("inputfilename", input_file_name())
        .withColumn(
            "filename",
            regexp_extract(
                col("inputfilename"),
                "(s3://)(.*)(/Inbound/raw/cdwa/ProviderInfo/)(.*)",
                4,
            ),
        )
        .withColumn(
            "filedate",
            to_date(
                regexp_extract(
                    col("filename"),
                    "(CDWA-O-BG-ProviderInfo-)(\d{4}-\d{2}-\d{2})(.csv)",
                    2,
                ),
                "yyyy-MM-dd",
            ),
        )
        .withColumn("cdwaid", col("person id"))
    )

    rawcdwadf.createOrReplaceTempView("cdwaproviderinfo")
    rawcdwadf.show()

    cdwaproviderinfo = spark.sql(
        """SELECT *
            FROM cdwaproviderinfo
            WHERE filedate > 
                (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date - 1)
                                        ELSE MAX(lastprocesseddate)
                                        END AS MAXPROCESSDATE
                            FROM vwlogslastprocessed
                            WHERE processname = 'glue-cdwa-s3-to-raw'
                                AND success = '1')
                    """
    )

    if cdwaproviderinfo.count() > 0:
        # Read all cdwaid's and SSN values from idcrosswalk table
        glueContext.create_dynamic_frame.from_catalog(
            database=catalog_database,
            table_name=catalog_table_prefix + "_staging_idcrosswalk",
        ).toDF().withColumn(
            "decryptssn", decrypt(col("fullssn"), lit(fernet_key))
        ).createOrReplaceTempView(
            "idcrosswalk"
        )

        # CDWA person IDs that have been found with duplicate SSN it is a hard error
        ssnduplicatedcdwaid = spark.sql(
            """SELECT cdwa.cdwaid FROM cdwaproviderinfo cdwa LEFT JOIN idcrosswalk ON cdwa.ssn = idcrosswalk.decryptssn WHERE cdwa.cdwaid != idcrosswalk.cdwaid"""
        )

        # Check for SSN length 7, 8, 9; if not, it is a hard error
        ssnerrorlenthcdwaid = spark.sql(
            """SELECT cdwa.cdwaid FROM cdwaproviderinfo cdwa WHERE length(ssn) < 7 OR length(ssn) > 9"""
        )

        # SSN Cannot be empty, it is a hard error
        ssnemptycdwaid = spark.sql(
            """SELECT cdwa.cdwaid FROM cdwaproviderinfo cdwa WHERE ssn is null"""
        )

        # Combining the Duplicate SSN & Check for SSN length not of size 7, 8, 9 & SSN Cannot be empty
        allssnerrorscdwaid = ssnduplicatedcdwaid.unionByName(
            ssnerrorlenthcdwaid
        ).unionByName(ssnemptycdwaid)

        # SSN Errors
        allssnerrorscdwaid.createOrReplaceTempView("allssnerrorscdwaid")

        # Filter with person IDs that have been found with allssnerrorscdwaid SSN
        cdwassnerrordf = spark.sql(
            """SELECT * FROM cdwaproviderinfo
                                        WHERE cdwaid IN (SELECT cdwaid FROM allssnerrorscdwaid)"""
        )

            
        torawcdwaduplicatessnerrors = cdwassnerrordf.selectExpr(
                "filedate", "filename", "cdwaid as personid"
            )
        
        torawcdwaduplicatessnerrors.write.jdbc(
                url=url,
                table="raw.cdwaduplicatessnerrors",
                mode=mode,
                properties=properties,
            )

        # Filter with person IDs that have been found without allssnerrorscdwaid SSN
        cdwaproviderinfoclean = spark.sql(
            """SELECT * FROM cdwaproviderinfo
                WHERE cdwaid NOT IN (SELECT cdwaid FROM allssnerrorscdwaid)"""
        )
        # Clean from SSN Errors
        cdwaproviderinfoclean.createOrReplaceTempView("cdwaproviderinfoclean")

        # Adding new caregivers to idcrosswalk table if the cdwaid does not exist in the idcrosswalk table
        idcrosswalktupdated_df = spark.sql(
            """SELECT DISTINCT * FROM cdwaproviderinfoclean A
                                                WHERE NOT EXISTS (SELECT 1 FROM idcrosswalk B WHERE A.cdwaid = B.cdwaid)"""
        )

        idcrosswalktupdated_df = idcrosswalktupdated_df.filter("ssn is not null")

        if idcrosswalktupdated_df.count() > 0:
            idcrosswalktupdated_df = idcrosswalktupdated_df.withColumn(
                "fullssn", encrypt("ssn", lit(fernet_key))
            )
            idcrosswalknewdatasource = DynamicFrame.fromDF(
                idcrosswalktupdated_df, glueContext, "idcrosswalknewdatasource"
            )
            idcrosswalkmapping = ApplyMapping.apply(
                frame=idcrosswalknewdatasource,
                mappings=[
                    ("fullssn", "string", "fullssn", "string"),
                    ("cdwaid", "string", "cdwaid", "long"),
                ],
            )
            glueContext.write_dynamic_frame.from_catalog(
                frame=idcrosswalkmapping,
                database=catalog_database,
                table_name=catalog_table_prefix + "_staging_idcrosswalk",
            )

        # Left Pad the ssn with 0 to make it 9 digits if < 9 digits & #last 4 digits of ssn
        cdwaproviderinfo = cdwaproviderinfo.withColumn(
            "ssn", format_string("%09d", col("ssn").cast("int"))
        ).withColumn("ssn", substring("ssn", 6, 4))
        cdwaproviderinfo = cdwaproviderinfo.withColumn(
            "mailing state", substring(upper(col("mailing state")), 1, 2)
        ).withColumn("physical state", substring(upper(col("physical state")), 1, 2))
        cdwaproviderinfocatalog = DynamicFrame.fromDF(cdwaproviderinfo, glueContext)
        cdwaproviderinfocatalogmapping = ApplyMapping.apply(
            frame=cdwaproviderinfocatalog,
            mappings=[
                ("employee id", "string", "employee_id", "bigint"),
                ("person id", "string", "personid", "string"),
                ("first name", "string", "first_name", "string"),
                ("Middle Name", "string", "middle_name", "string"),
                ("last name", "string", "last_name", "string"),
                ("ssn", "string", "ssn", "string"),
                ("dob", "string", "dob", "int"),
                ("gender", "string", "gender", "string"),
                ("race", "string", "race", "string"),
                ("language", "string", "language", "string"),
                ("Marital Status", "string", "marital_status", "string"),
                ("phone 1", "string", "phone_1", "long"),
                ("phone 2", "string", "phone_2", "long"),
                ("email", "string", "email", "string"),
                ("mailing add 1", "string", "mailing_add_1", "string"),
                ("mailing add 2", "string", "mailing_add_2", "string"),
                ("mailing city", "string", "mailing_city", "string"),
                ("mailing state", "string", "mailing_state", "string"),
                ("mailing zip", "string", "mailing_zip", "string"),
                ("physical add 1", "string", "physical_add_1", "string"),
                ("physical add 2", "string", "physical_add_2", "string"),
                ("physical city", "string", "physical_city", "string"),
                ("physical state", "string", "physical_state", "string"),
                ("physical zip", "string", "physical_zip", "string"),
                ("Employee Classification","string","employee_classification","string"),
                ("exempt status", "string", "exempt_status", "string"),
                ("Background Check Date", "string", "background_check_date", "int"),
                ("i&e date", "string", "ie_date", "int"),
                ("hire date", "string", "hire_date", "int"),
                ("classification start date","string","classification_start_date","int"),
                ("carina eligible", "string", "carina_eligible", "string"),
                ("ahcas eligible", "string", "ahcas_eligible", "string"),
                ("o&s completed", "string", "os_completed", "int"),
                ("termination date", "string", "termination_date", "int"),
                ("authorized start date", "string", "authorized_start_date", "int"),
                ("authorized end date", "string", "authorized_end_date", "int"),
                ("client count", "string", "client_count", "int"),
                ("Client Relationship", "string", "client_relationship", "string"),
                ("Client ID", "string", "client_id", "string"),
                ("filename", "string", "filename", "string"),
                ("Ethnicity", "string", "ethnicity", "string"),
                ("filedate", "date", "filemodifieddate", "date"),
            ],
        )

        glueContext.write_dynamic_frame.from_catalog(
            frame=cdwaproviderinfocatalogmapping,
            database=catalog_database,
            table_name=catalog_table_prefix + "_raw_cdwa",
        )

        # WRITE a record with process/execution time to logs.lastprocessed table
        lastprocessed_df = spark.createDataFrame(
            [("glue-cdwa-s3-to-raw", cdwaproviderinfoclean.first()["filedate"], "1")],
            schema=["processname", "lastprocesseddate", "success"],
        )

        # Create Dynamic Frame to log lastprocessed table
        lastprocessed_cdf = DynamicFrame.fromDF(
            lastprocessed_df, glueContext, "lastprocessed_cdf"
        )

        lastprocessed_cdf_applymapping = ApplyMapping.apply(
            frame=lastprocessed_cdf,
            mappings=[
                ("processname", "string", "processname", "string"),
                ("lastprocesseddate", "date", "lastprocesseddate", "timestamp"),
                ("success", "string", "success", "string"),
            ],
        )

        # Write to postgresql logs.lastprocessed table of the success
        glueContext.write_dynamic_frame.from_catalog(
            frame=lastprocessed_cdf_applymapping,
            database=catalog_database,
            table_name=f"{catalog_table_prefix}_logs_lastprocessed",
        )
    else:
        print("File has already processed or no records in the file.")

    # Moving the processed file to archive location
    sourcekey = processingfilekey
    targetkey = sourcekey.replace("/raw/", "/archive/")
    copy_source = {"Bucket": S3_BUCKET, "Key": sourcekey}
    s3bucket.copy(copy_source, targetkey)
    s3resource.Object(S3_BUCKET, sourcekey).delete()


job.commit()
