import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
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


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node PostgreSQL table
PostgreSQLtable_node1 = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix + "_staging_vw_getproviderinfo",
    transformation_ctx="PostgreSQLtable_node1",
)
rawcdwaDF = PostgreSQLtable_node1.toDF()
rawcdwaDF.printSchema()

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix + "_prod_branch",
).toDF().selectExpr("employerid", "branchid").createOrReplaceTempView("branch")

rawcdwaDF = rawcdwaDF.withColumn(
    "employerid", col("employerid").cast("int")
).withColumn("createdby", lit("cdwa-employementrelationshiphistory-gluejob"))
rawcdwaDF.select("employerid").show()
rawcdwaDF = rawcdwaDF.withColumn("role", (lit("CARE")))
rawcdwaDF.printSchema()

branchdf = spark.sql("select * from branch")
# joining rawcdwaDF and branchdf to get branchid
joinedDF = rawcdwaDF.join(branchdf, on="employerid", how="left")

PostgreSQLtable_node2 = DynamicFrame.fromDF(
    joinedDF, glueContext, "PostgreSQLtable_node2"
)

# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=PostgreSQLtable_node2,
    mappings=[
        ("sourcekey", "string", "source", "string"),
        ("classificationcode", "string", "categorycode", "string"),
        ("filedate", "date", "filedate", "date"),
        ("initialtrackingdate", "date", "trackingdate", "string"),
        ("createdby", "string", "createdby", "string"),
        ("hire_date", "date", "hiredate", "timestamp"),
        ("priority", "int", "priority", "int"),
        ("employerid", "int", "employerid", "string"),
        ("branchid", "int", "branchid", "int"),
        ("authorized_end_date", "timestamp", "authend", "string"),
        ("termination_date", "timestamp", "terminationdate", "string"),
        ("authorized_start_date", "timestamp", "authstart", "string"),
        ("employee_id", "decimal", "employeeid", "bigint"),
        ("employee_classification", "string", "workercategory", "string"),
        ("relationship", "string", "relationship", "string"),
        ("empstatus", "string", "empstatus", "string"),
        ("role", "string", "role", "string"),
    ],
    transformation_ctx="ApplyMapping_node2",
)
ApplyMapping_node2.toDF().show()


# Script generated for node PostgreSQL table
PostgreSQLtable_node3 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database=catalog_database,
    table_name=catalog_table_prefix + "_staging_employmentrelationshiphistory",
    transformation_ctx="PostgreSQLtable_node3",
)


# WRITE a record with process/execution time to logs.lastprocessed table
lastprocessed_df = spark.createDataFrame(
    [("glue-cdwa-raw-to-staging-employementrelationshiphistory", datetime.now(), "1")],
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
        ("lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"),
        ("success", "string", "success", "string"),
    ],
)

lastprocessed_cdf_applymapping.show()

# Write to PostgreSQL logs.lastprocessed table of the success
PostgreSQLtable_node4 = glueContext.write_dynamic_frame.from_catalog(
    frame=lastprocessed_cdf_applymapping,
    database=catalog_database,
    table_name=catalog_table_prefix + "_logs_lastprocessed",
    transformation_ctx="PostgreSQLtable_node4",
)

job.commit()
