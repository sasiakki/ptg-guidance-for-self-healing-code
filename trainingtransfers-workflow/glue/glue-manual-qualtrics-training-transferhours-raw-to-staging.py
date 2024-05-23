import sys
from awsglue.transforms import *
from awsglue.transforms import ApplyMapping
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import concat, col, when
from datetime import datetime
import boto3
import json

#Default Job Arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name= catalog_table_prefix+"_raw_qualtrics_transfer_hours"
).toDF().selectExpr("*").createOrReplaceTempView("rawqualtricstrainingtransfers")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_prod_person"
).toDF().selectExpr("*")\
    .createOrReplaceTempView("person")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_prod_trainingrequirement"
).toDF().selectExpr("*")\
    .createOrReplaceTempView("trainingrequirement")

training_df = spark.sql("""select * from rawqualtricstrainingtransfers""")
## Add the timestamp from log.lastprocessed and only extract the today's data

## B2BDS-1385: loglast DF
logslastprocesseddf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "logsdf")
logslastprocesseddf = logslastprocesseddf.toDF().createOrReplaceTempView("logslastprocessed")

# training_df = training_df.createOrReplaceTempView("rawqualtricstrainingtransfersdata")
training_df = spark.sql("""SELECT * FROM rawqualtricstrainingtransfers WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                END AS MAXPROCESSDATE FROM logslastprocessed  WHERE processname='glue-manual-qualtrics-training-transferhours-raw-to-staging' AND success='1')""")

# from pyspark.sql.functions import when
training_df = training_df.withColumn("trainingprogramcode",
       when((col("coursename") == "Basic Training 70 Hours (BT70)") & (col("credits") == 70), "201")
      .when((col("coursename") == "Basic Training 30 Hours (BT30)") & (col("credits") == 30), "202")
      .when((col("coursename") == "Basic Training 9 Hours (BT9)") & (col("credits") == 9), "203")
      .when((col("coursename") == "Basic Training 7 Hours (BT7)") & (col("credits") == 7), "204")
      .when((col("coursename") == "Orientation & Safety (O&S)") & (col("credits") == 5), "100")
      .when(~(col("coursename").like("Basic Training%")) & ~(col("coursename").like("Orientation%Safety%")) & (col("credits") >= 0) & (col("credits") <= 12), "300")
      )

training_df = training_df.withColumn("trainingprogram",
       when((col("coursename") == "Basic Training 70 Hours (BT70)") & (col("credits") == 70), "Basic Training 70")
      .when((col("coursename") == "Basic Training 30 Hours (BT30)") & (col("credits") == 30), "Basic Training 30")
      .when((col("coursename") == "Basic Training 9 Hours (BT9)") & (col("credits") == 9), "Basic Training 9")
      .when((col("coursename") == "Basic Training 7 Hours (BT7)") & (col("credits") == 7), "Basic Training 7")
      .when((col("coursename") == "Orientation & Safety (O&S)") & (col("credits") == 5), "Orientation and Safety")
      .when(~(col("coursename").like("Basic Training%")) & ~(col("coursename").like("Orientation%Safety%")) & (col("credits") >= 0) & (col("credits") <= 12), "Continuing Education")
      )

training_df.createOrReplaceTempView("qualtricstrainingtransfers")

spark.sql("""select personid,trainingprogramcode,trainingid,cast(trackingdate as date) as trackingdate,cast(duedate as date) as duedate,
cast(duedateextension as date) as duedateextension from trainingrequirement where lower(status) = 'active'""").createOrReplaceTempView("trainingrequirement")

spark.sql(""" select personid, cast(hiredate as date) as hiredate from person """).createOrReplaceTempView("person")


spark.sql(""" 
with cte_a as (select ctt.*,pt.trainingid,
                pt.trackingdate,
                pt.duedate,
                pt.duedateextension,
                pp.hiredate from qualtricstrainingtransfers ctt left join trainingrequirement pt  on ctt.personid = pt.personid and ctt.trainingprogramcode = pt.trainingprogramcode
left join person pp on ctt.personid = pp.personid
)select *, case when trainingprogram is null then 'Invalid transfer credit hours received'
		   when hiredate is not null and cast(completed as date)  < hiredate then 'Completion date should be greater than the hire date'
           when trainingid is null then 'No open training requirement exist'
           when trainingid is not null and cast(completed as date) NOT BETWEEN trackingdate AND coalesce(duedateextension,duedate) then 'Completion should not exceed due date or due date extension' end as error_message
           from cte_a
""").createOrReplaceTempView("transfers_validation_view")


log_transfers_df = spark.sql(""" select * from transfers_validation_view where error_message is not null """)
staging_transfers_df = spark.sql(""" select * from transfers_validation_view where error_message is null """)

staging_transfers_df.show()
log_transfers_df.show()
#staging_transfers_df.count()
# log_transfers_df.count()

stagingtransfers = DynamicFrame.fromDF(staging_transfers_df, glueContext, "stagingtransfers")

# Script generated for node ApplyMapping
validtransfers_targetmapping = ApplyMapping.apply(
    frame=stagingtransfers,
    mappings=[
        
        ("personid", "string", "personid", "bigint"),
        ("trainingprogram", "string", "trainingprogram", "string"),
         ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("credits", "string", "transferhours", "numeric"),
        ("completed", "timestamp", "completeddate", "date"),
        ("reason_code", "string", "reasonfortransfer", "string"),
        ("dshsid", "string", "dshscoursecode", "string"),
        ("source","string","transfersource","string"),
        ("coursename","string","classname","string"),
        ("courseid","string","courseid","string")]
)


#Appending all valid records to staging training transfers 
glueContext.write_dynamic_frame.from_catalog(
    frame=validtransfers_targetmapping,
    database=catalog_database,
    table_name=catalog_table_prefix+"_staging_trainingtransfers",
)

transferslogs = DynamicFrame.fromDF(log_transfers_df, glueContext, "transferslogs")

errortransfer_targetmapping = ApplyMapping.apply(
    frame=transferslogs,
    mappings=[
        ("personid", "string", "personid", "bigint"),
        ("trainingprogram", "string", "trainingprogram", "string"),
        ("credits", "string", "credithours", "string"),
        ("completed", "timestamp", "completeddate", "date"),
        ("source", "string", "trainingentity", "string"),
        ("reason_code", "string", "reasonfortransfer", "string"),
        ("finished","string","isvalid","boolean"),
        ("employerstaff", "string", "employerstaff", "string"),
        ("dshsid", "string", "dshscoursecode", "string"),
        ("error_message","string","error_message","string"),
        ("coursename","string","classname","string"),
        ("filename","string","filename","string"),
        ("filedate","date","filedate","date"),
    ],
)

# Appending all error to training transfers logs
glueContext.write_dynamic_frame.from_catalog(
    frame=errortransfer_targetmapping,
   database=catalog_database,
    table_name=catalog_table_prefix+"_logs_trainingtransferslogs",
)

## B2BDS-1385: insert an entry into the log
# WRITE a record with process/execution time to logs.lastprocessed table
lastprocessed_df = spark.createDataFrame(
    [('glue-manual-qualtrics-training-transferhours-raw-to-staging', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])

# Create Dynamic Frame to log lastprocessed table
lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext,"lastprocessed_cdf")
lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[("processname", "string", "processname", "string"), (
    "lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"), ("success", "string", "success", "string")])

# Write to postgresql logs.lastprocessed table of the success
glueContext.write_dynamic_frame.from_catalog(
    frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")

job.commit()