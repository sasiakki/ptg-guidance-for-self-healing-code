import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col,to_date,current_timestamp,regexp_extract

    
args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# Initialize GlueContext and SparkSession
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix +"_raw_dohclassified").toDF().createOrReplaceTempView("raw_doh_classified")
spark.sql(""" select * from raw_doh_classified """).show(truncate=False)
glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_dohclassified").toDF().createOrReplaceTempView("prod_doh_classified")
spark.sql(""" select * from prod_doh_classified """).show(truncate=False)

lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, 
    table_name=catalog_table_prefix+"_logs_lastprocessed"
 ).toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")



# Query for dedup logic(Eliminating duplicates) in the raw
dedup_df = spark.sql("""with cte as (select * ,ROW_NUMBER() OVER ( PARTITION BY credentialnumber ORDER BY filereceiveddate ASC ) completionsrank from raw_doh_classified) select * from cte where completionsrank = 1 AND recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-doh-classified-raw-to-prod' AND success='1')""")

# create a temporary view in for the dedup_df DataFrame
dedup_df.createOrReplaceTempView("doh_classified_dedup")
dedup_df.show(truncate=False)
dedup_df_count = dedup_df.count()
print(f"Number of rows in Deduplicate DataFrame in Raw Doh Classified: {dedup_df_count}")

# query to check if the record already exists in prod.doh and not writing it again and if not insert 
updated_df = spark.sql(
    """select distinct * from doh_classified_dedup A where not EXISTS (Select 1 from prod_doh_classified B where A.credentialnumber = B.credentialnumber)""")
updated_df.show(truncate=False)
updatedp_df_count = updated_df.count()
print(f"Number of rows in updated DataFrame : {updatedp_df_count}")

updated_df = updated_df.withColumn("filereceiveddate",to_date("filereceiveddate",'MM/dd/yyyy'))\
                       .withColumn("applicationdate",to_date(col('applicationdate'),'MM/dd/yyyy'))\
                       .withColumn("datedshsbenefitpaymentudfupdated",to_date(col('datedshsbenefitpaymentudfupdated'),'MM/dd/yyyy'))\
                       .withColumn("recordmodifieddate",current_timestamp())\
                       .withColumn("classifieddate",to_date(regexp_extract(col("filename"),'(DSHS Benefit Classified File )(\d\d\d\d\d\d\d\d\d\d\d\d\d\d)(.csv)',2),"yyyyMMddHHmmss"))\
                    
updated_df.show(truncate=False)
updated_df.printSchema()

if ( updated_df.count() > 0 ):
    newdatasource_doh_classified = DynamicFrame.fromDF(updated_df, glueContext, "newdatasource_doh_classified")
    # Script generated for node Apply Mapping
    applymapping_prod_doh_classified = ApplyMapping.apply(
        frame=newdatasource_doh_classified,
        mappings=[
            ("filefirstname", "string", "filefirstname", "string"),
            ("filelastname", "string", "filelastname", "string"),
            ("filename", "string", "filename", "string"),
            ("filereceiveddate", "date", "filereceiveddate", "date"),
            ("dohname", "string", "dohname", "string"),
            ("credentialnumber", "string", "credentialnumber", "string"),
            ("credentialstatus", "string", "credentialstatus", "string"),
            ("applicationdate", "date", "applicationdate", "date"),
            ("datedshsbenefitpaymentudfupdated", "date", "datedshsbenefitpaymentudfupdated", "date"),
            ("classifieddate", "date", "classifieddate", "date"),
            ("recordmodifieddate", "timestamp", "recordmodifieddate", "timestamp"),
        ],
        transformation_ctx="applymapping_prod_doh_classified",
    )
    
    # Script generated for node Select Fields
    selectfields_prod_doh_classified = SelectFields.apply(
        frame=applymapping_prod_doh_classified,
        paths=[
            "filefirstname",
            "filelastname",
            "filereceiveddate",
            "dohname",
            "credentialnumber",
            "credentialstatus",
            "applicationdate",
            "datedshsbenefitpaymentudfupdated",
            "classifieddate",
            "recordmodifieddate",
        ],
        transformation_ctx="SelectFields_node1646956724845",
    )
    dropNullfields_prod_doh_classified = DropNullFields.apply(frame = selectfields_prod_doh_classified)
    
    # Script generated for node AWS Glue Data Catalog
    glueContext.write_dynamic_frame.from_catalog(
        frame=dropNullfields_prod_doh_classified,
        database=catalog_database,
        table_name=catalog_table_prefix+"_prod_dohclassified",
    )
    
    print("Insert an entry into the log table")    
    # WRITE a record with process/execution time to logs.lastprocessed table
    max_date = datetime.now()
    lastprocessed_df = spark.createDataFrame(
        [("glue-doh-classified-raw-to-prod", max_date, "1")],
        schema=["processname", "lastprocesseddate", "success"],
    )

    lastprocessed_df.show()

    # Create Dynamic Frame to log lastprocessed table
    lastprocessed_cdf = DynamicFrame.fromDF(
    lastprocessed_df, glueContext, "lastprocessed_cdf")
    lastprocessed_cdf_applymapping = ApplyMapping.apply(
    frame=lastprocessed_cdf,
    mappings=[
            ("processname", "string", "processname", "string"),
            ("lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"),
            ("success", "string", "success", "string"),
            ],
        )

    # Write to postgresql logs.lastprocessed table of the success
    glueContext.write_dynamic_frame.from_catalog(
        frame=lastprocessed_cdf_applymapping,
        database=catalog_database,
        table_name=f"{catalog_table_prefix}_logs_lastprocessed",
            )

#uncomment the below line if it is commented out for testing
job.commit()