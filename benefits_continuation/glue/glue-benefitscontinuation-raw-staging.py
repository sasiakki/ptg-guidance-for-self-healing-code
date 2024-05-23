import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import lit 
import pandas as pd
from pyspark.sql.functions import *
from datetime import datetime
log_time=datetime.now()

#Default Job Arguments
## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']
if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'


raw_ip_benefitscontinuation_df = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_ip_benefitscontinuation").toDF()
# Create the Glue Catalog Temp Table LastProcessed Tables
logs_lastprocessed = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed").toDF()
logs_lastprocessed.createOrReplaceTempView("lastprocessed")
raw_ip_benefitscontinuation_df.createOrReplaceTempView("raw_ip_benefitscontinuation")
raw_ip_benefitscontinuation_df=spark.sql("""select * from raw_ip_benefitscontinuation where recordmodifieddate > (select case
                    when max(lastprocesseddate) is null then (current_date -1)
                    else max(lastprocesseddate)
                    end as maxprocessdate
                    from lastprocessed
                    where processname= 'glue-benefitscontinuation-raw-staging'
                    and success= '1' )""")

dataframe = raw_ip_benefitscontinuation_df.toPandas()

dataframe['bcapproveddate']=pd.to_datetime(dataframe['bcapproveddate'],format='%Y%m%d')
dataframe['duedateoverride']=pd.to_datetime(dataframe['duedateoverride'],format='%Y%m%d')
dataframe['bgpersonid'] = dataframe['bgpersonid'].astype('int64')
dataframe = spark.createDataFrame(dataframe)



# adding required additional columns to CDWA_person df.
raw_CDWA_final_df=dataframe.withColumn('file_source',lit('raw_IP'))

DataCatalogtable_node2 = DynamicFrame.fromDF(raw_CDWA_final_df, glueContext, "DataCatalogtable_node2")
# Script generated for node ApplyMapping
ApplyMapping_node2 = ApplyMapping.apply(
    frame=DataCatalogtable_node2,
    mappings=[
            ("bgpersonid", "long", "personid", "bigint"),
            ("employerrequested", "string", "employerrequested", "string"),
            ("firstname", "string", "firstname", "string"),
            ("lastname", "string", "lastname", "string"),
            ("email", "string", "email", "string"),
            ("bcapproveddate", "timestamp", "bcapproveddate", "timestamp"),
            ("duedateoverride", "timestamp", "duedateoverride", "timestamp"),
            ("duedateoverridereason", "string", "duedateoverridereason", "string"),
            ("File_source", "string", "File_source", "string"),
            ("trainingname", "string", "trainingname", "string")
           
    ],
    transformation_ctx="ApplyMapping_node2",
)


# Script generated for node PostgreSQL table
PostgreSQLtable_node3 = glueContext.write_dynamic_frame.from_catalog(
    frame=ApplyMapping_node2,
    database = catalog_database,  
    table_name = catalog_table_prefix +"_staging_benefitscontinuation",
    transformation_ctx="PostgreSQLtable_node3",
)


# WRITE a record with process/execution time to logs.lastprocessed table
lastprocessed_df = spark.createDataFrame(
    [('glue-benefitscontinuation-raw-staging', log_time, "1")], schema=["processname", "lastprocesseddate", "success"])
# Create Dynamic Frame to log lastprocessed table
lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext, "lastprocessed_cdf")
lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[
    ("processname", "string", "processname", "string"),
    ("lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"),
    ("success", "string", "success", "string")])

# Write to PostgreSQL logs.lastprocessed table of the success
PostgreSQLtable_node4 = glueContext.write_dynamic_frame.from_catalog(
    frame=lastprocessed_cdf_applymapping,
    database=catalog_database,
    table_name=catalog_table_prefix+"_logs_lastprocessed",
    transformation_ctx="PostgreSQLtable_node4",
)

job.commit()