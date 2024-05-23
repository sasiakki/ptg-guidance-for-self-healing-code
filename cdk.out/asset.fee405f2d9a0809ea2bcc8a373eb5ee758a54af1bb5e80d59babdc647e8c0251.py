import sys
import boto3
import json
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from datetime import datetime

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account["environment_type"]

if environment_type == "dev":
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client("secretsmanager")

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

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

credential_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix + "_raw_credential_delta",
    transformation_ctx="datasource0",
).toDF()

newdatasource_credential = DynamicFrame.fromDF(
    credential_df, glueContext, "newdatasource_credential"
)
# Script generated for node ApplyMapping
applymapping_credential = ApplyMapping.apply(
    frame=newdatasource_credential,
    mappings=[
        ("credentialtype", "string", "credentialtype", "string"),
        ("paymentdate", "string", "paymentdate", "string"),
        (
            "limitedenglishproficiencyindicator",
            "string",
            "limitedenglishproficiencyindicator",
            "string",
        ),
        ("credentialstatus", "string", "credentialstatus", "string"),
        ("primarycredential", "int", "primarycredential", "int"),
        ("longtermcareworkertype", "string", "longtermcareworkertype", "string"),
        ("dateofhire", "string", "dateofhire", "string"),
        ("actiontaken", "string", "actiontaken", "string"),
        (
            "excludedlongtermcareworker",
            "string",
            "excludedlongtermcareworker",
            "string",
        ),
        ("taxid", "int", "taxid", "int"),
        ("examscheduledsitename", "string", "examscheduledsitename", "string"),
        ("providernumber", "long", "providernumber", "long"),
        ("examdtrecdschedtestdate", "string", "examdtrecdschedtestdate", "string"),
        ("providernamedoh", "string", "providernamedoh", "string"),
        ("examemailaddress", "string", "examemailaddress", "string"),
        ("providernamedshs", "string", "providernamedshs", "string"),
        ("dateofbirth", "string", "dateofbirth", "string"),
        (
            "credentiallastdateofcontact",
            "string",
            "credentiallastdateofcontact",
            "string",
        ),
        ("recordcreateddate", "timestamp", "recordcreateddate", "timestamp"),
        ("lastissuancedate", "string", "lastissuancedate", "string"),
        ("examtestertype", "string", "examtestertype", "string"),
        ("examscheduleddate", "string", "examscheduleddate", "string"),
        ("phonenum", "string", "phonenum", "string"),
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("expirationdate", "string", "expirationdate", "string"),
        ("lepprovisionalcredential", "string", "lepprovisionalcredential", "string"),
        (
            "continuingeducationduedate",
            "string",
            "continuingeducationduedate",
            "string",
        ),
        ("personid", "long", "personid", "long"),
        ("examscheduledsitecode", "string", "examscheduledsitecode", "string"),
        (
            "lepprovisionalcredentialexpirationdate",
            "string",
            "lepprovisionalcredentialexpirationdate",
            "string",
        ),
        (
            "lepprovisionalcredentialissuedate",
            "string",
            "lepprovisionalcredentialissuedate",
            "string",
        ),
        ("preferredlanguage", "string", "preferredlanguage", "string"),
        ("firstissuancedate", "string", "firstissuancedate", "string"),
        ("credentialstatusdate", "string", "credentialstatusdate", "string"),
        ("nctrainingcompletedate", "string", "nctrainingcompletedate", "string"),
        ("recordmodifieddate", "timestamp", "recordmodifieddate", "timestamp"),
        ("dohcertduedate", "date", "dohcertduedate", "date"),
    ],
    transformation_ctx="ApplyMapping_node2",
)
##########################Overwrite script - start ####################################

final_df = applymapping_credential.toDF()
# final_df = new_df
print("final_df count")
print(final_df.count())

final_df.show(20, truncate=False)
final_df.printSchema()


final_df.write.option("truncate", True).jdbc(
    url=url, table="prod.credential", mode=mode, properties=properties
)

print("completed writing")

##########################Overwrite script - end ####################################

print("Insert an entry into the log table")
max_filedate = datetime.now()
logs_data = [[max_filedate, "glue-credentials-delta-to-Prodcredentials", "1"]]
logs_columns = ["lastprocesseddate", "processname", "success"]
logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
mode = "append"
logs_dataframe.write.jdbc(
    url=url, table="logs.lastprocessed", mode=mode, properties=properties
)


job.commit()
