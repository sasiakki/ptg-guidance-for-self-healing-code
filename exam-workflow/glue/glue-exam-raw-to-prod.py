import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import to_date,col,coalesce,when
from awsglue.dynamicframe import DynamicFrame

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

# Script for node PostgreSQL read from raw exam table
raw_examcdf = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_raw_exam",
    transformation_ctx="raw_examcdf",
)
# Converting the multiple formats of date to single date datatype
raw_examdf = raw_examcdf.toDF().withColumn("examdate", coalesce(
    *[to_date("examdate", f) for f in ("MM/dd/yy", "MM/dd/yyyy", "MM-dd-yyyy", "MMddyyyy")]))

# infering blanks to nulls
raw_examdf = raw_examdf.select([when(col(c) == "", None).otherwise(
    col(c)).alias(c) for c in raw_examdf.columns])

# Filtering isdelta true records in raw table
raw_examdf = raw_examdf.filter(col("isdelta") == True)

raw_examdf.createOrReplaceTempView("rawexam")

# Script for node PostgreSQL  read from prod exam table
prod_examcdf = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_prod_exam",
    transformation_ctx="prod_examcdf",
)
# Converting the multiple formats of date to single date datatype
prod_examdf = prod_examcdf.toDF().withColumn("examdate", coalesce(
    *[to_date("examdate", f) for f in ("MM/dd/yy", "MM/dd/yyyy", "MM-dd-yyyy", "MMddyyyy")]))

# infering balanks to nulls
prod_examdf = prod_examdf.select([when(col(c) == "", None).when(
    col(c) == "NULL", None).otherwise(col(c)).alias(c) for c in prod_examdf.columns])

examdatasource = DynamicFrame.fromDF(raw_examdf, glueContext, "datasource0")

# ApplyMapping to match the target table
applymapping_exam_prod = ApplyMapping.apply(
    frame=examdatasource,
    mappings=[
        ("recordcreateddate", "timestamp", "recordcreateddate", "timestamp"),
        ("filename", "string", "filename", "string"),
        ("filemodifieddate", "timestamp", "filemodifieddate", "timestamp"),
        ("examstatus", "string", "examstatus", "string"),
        ("testlanguage", "string", "testlanguage", "string"),
        ("testsite", "string", "testsite", "string"),
        ("randomskill1result", "string", "randomskill1result", "string"),
        ("credentialnumber", "string", "credentialnumber", "string"),
        ("studentid", "string", "studentid", "string"),
        ("promotingsafety", "string", "promotingsafety", "string"),
        ("randomskill2result", "string", "randomskill2result", "string"),
        ("commoncarepracticesskillresult", "string",
         "commoncarepracticesskillresult", "string"),
        ("randomskill3result", "string", "randomskill3result", "string"),
        ("taxid", "string", "taxid", "string"),
        ("examtitlefromprometrics", "string", "examtitlefromprometrics", "string"),
        ("sitename", "string", "sitename", "string"),
        ("examdate", "date", "examdate", "string"),
        ("supportingphysicalandpsychosocialwellbeing", "string",
         "supportingphysicalandpsychosocialwellbeing", "string"),
        ("handwashingskillresult", "string", "handwashingskillresult", "string"),
        ("rolesandresponsibilitiesofthehomecareaide", "string",
         "rolesandresponsibilitiesofthehomecareaide", "string"),
        ("recordmodifieddate", "timestamp", "recordmodifieddate", "timestamp")
    ],
    transformation_ctx="applymapping_exam_prod",
)
# Script for node PostgreSQL to write to  prod exam table

glueContext.write_dynamic_frame.from_catalog(
    frame=applymapping_exam_prod,
    database=catalog_database,
    table_name=catalog_table_prefix+"_prod_exam",
)
job.commit()
