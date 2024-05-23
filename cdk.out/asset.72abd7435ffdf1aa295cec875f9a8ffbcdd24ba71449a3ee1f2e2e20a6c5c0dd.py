import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import split, col, lit, concat, to_date, current_timestamp, regexp_extract

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix +
                                              "_raw_dohcompleted").toDF().createOrReplaceTempView("raw_doh_complete")
spark.sql(""" select * from raw_doh_complete """).show(truncate=False)

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=catalog_table_prefix+"_prod_dohcompleted").toDF().createOrReplaceTempView("prod_doh_complete")

spark.sql(""" select * from prod_doh_complete """).show(truncate=False)

# Query for dedup logic(Eliminating duplicates) in the raw
dedup_df = spark.sql("""with cte as (select * ,ROW_NUMBER() OVER ( PARTITION BY credentialnumber ORDER BY filereceiveddate ASC ) completionsrank from raw_doh_complete) select * from cte where completionsrank = 1""")
# create a temporary view in for the dedup_df DataFrame
dedup_df.createOrReplaceTempView("doh_completed_dedup")
dedup_df.show(truncate=False)
dedup_df_count = dedup_df.count()
print(f"Number of rows in Deduplicate DataFrame in Raw: {dedup_df_count}")

# query to check if the record already exists in prod.doh and not writing it again and if not insert·
updated_df = spark.sql(
    """select distinct * from doh_completed_dedup A where not EXISTS (Select 1 from prod_doh_complete B where A.credentialnumber = B.credentialnumber)""")
updated_df.show(truncate=False)
updatedp_df_count = updated_df.count()
print(f"Number of rows in updated DataFrame: {updatedp_df_count}")


updated_df.select(
    split(col("approvedinstructorcodeandname"), "\s+").getItem(0)).show()
updated_df.select(concat(split(col("approvedinstructorcodeandname"), "\s+").getItem(1),
                  lit(" "), split(col("approvedinstructorcodeandname"), "\s+").getItem(2))).show()
updated_df = updated_df.withColumn("filereceiveddate", to_date("filereceiveddate", 'MM/dd/yyyy'))\
                       .withColumn("applicationdate", to_date(col('applicationdate'), 'MM/dd/yyyy'))\
                       .withColumn("dateinstructorupdated", to_date(col('dateapprovedinstructorcodeandnameudfupdated'), 'MM/dd/yyyy'))\
                       .withColumn("dategraduatedfor70hours", to_date(col('dategraduatedfor70hours'), 'MM/dd/yyyy'))\
                       .withColumn("recordmodifieddate", current_timestamp())\
                       .withColumn("approvedinstructorcode", split(col("approvedinstructorcodeandname"), "\s+").getItem(0))\
                       .withColumn("approvedinstructorname", concat(split(col("approvedinstructorcodeandname"), "\s+").getItem(1), lit(" "), split(col("approvedinstructorcodeandname"), "\s+").getItem(2)))\
                       .withColumn("completeddate", to_date(regexp_extract(col("filename"), '(DSHS Benefit Training Completed File )(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)', 2), "yyyyMMddHHmmss"))

newdatasource_doh_completed = DynamicFrame.fromDF(
    updated_df, glueContext, "newdatasource_doh_completed")

applymapping_doh_completed = ApplyMapping.apply(frame=newdatasource_doh_completed, mappings=[("filefirstname", "string", "filefirstname", "string"),  ("filelastname", "string", "filelastname", "string"),  ("credentialstatus", "string", "credentialstatus", "string"), ("filereceiveddate", "date", "filereceiveddate", "date"), ("credentialnumber", "string", "credentialnumber", "string"), ("dohname", "string", "dohname", "string"), ("approvedinstructorcode", "string", "approvedinstructorcode", "string"), (
    "approvedinstructorname", "string", "approvedinstructorname", "string"), ("applicationdate", "date", "applicationdate", "date"), ("completeddate", "date", "completeddate", "date"), ("dateinstructorupdated", "date", "dateinstructorupdated", "date"), ("filename", "string", "filename", "string"), ("dategraduatedfor70hours", "date", "dategraduatedfor70hours", "date"), ("recordmodifieddate", "timestamp", "recordmodifieddate", "timestamp")], transformation_ctx="applymapping_doh_completed")

selectfields_doh_completed = SelectFields.apply(frame=applymapping_doh_completed, paths=["filefirstname", "filelastname", "credentialstatus", "completeddate", "filereceiveddate", "credentialnumber", "dohname",
                                                                                         "approvedinstructorname", "approvedinstructorcode", "applicationdate", "dateinstructorupdated",  "dategraduatedfor70hours", "recordmodifieddate"], transformation_ctx="selectfields_doh_completed")

dropNullfields_doh_completed = DropNullFields.apply(
    frame=selectfields_doh_completed)


glueContext.write_dynamic_frame.from_catalog(
    frame=dropNullfields_doh_completed, database=catalog_database, table_name=catalog_table_prefix+"_prod_dohcompleted")
# uncomment the below line if it is commented out for testing
job.commit()
