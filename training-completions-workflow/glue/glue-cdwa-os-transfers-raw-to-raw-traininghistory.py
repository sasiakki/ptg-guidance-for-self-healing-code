import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import boto3
import json


## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'


# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

s3_client = boto3.client('s3')

#Creating Temp View for cdwaoandstransfers table in prod schema														  
cdwaostransfersdf = glueContext.create_dynamic_frame.from_catalog(
                        database = catalog_database, 
                        table_name = catalog_table_prefix+"_raw_cdwatrainingtransfers"
                        ).toDF().createOrReplaceTempView("rawcdwatrainingtransfers")


#Creating Temp View for person table in prod schema																																									   
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=catalog_table_prefix+"_prod_person"
).toDF().selectExpr("*").createOrReplaceTempView("person")

#Access the lastprocessed log table and create a DF for Delta Detection purpose
logslastprocesseddf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "logsdf")
logslastprocesseddf = logslastprocesseddf.toDF().createOrReplaceTempView("logslastprocessed")

#Insert into raw table only if data from the source table has filedate > lastprocesseddate based on the log table
cdwaostransfersdf = spark.sql("""SELECT * FROM rawcdwatrainingtransfers WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM logslastprocessed WHERE processname='glue-cdwa-os-transfers-raw-to-raw-traininghistory' AND success='1')""")

#Only proceed if new data are detected. If the data already existed (filedate <= last processed date), then archive 
if (cdwaostransfersdf.count() > 0):
    cdwaostransfersdf.createOrReplaceTempView("rawcdwatrainingtransfers")
    #within the cdwaoandstransfers table on personid,trainingprogram  with earliest completed date.
    spark.sql("""select *,
        'Orientation & Safety EN' as coursename ,
        5 as credit_hours ,
        '1000065ONLEN02' as courseid ,
        100 as trainingprogramcode ,
        'Orientation & Safety' as trainingprogramtype ,
        'EN' as courselanguage,
        'ONL' as coursetype,
        'CDWA' as trainingsource,
        'instructor' as instructorname,
        'instructor' as instructorid, ROW_NUMBER() OVER ( PARTITION BY personid, trainingprogram ORDER BY completeddate ASC ) completionsrank 
        from rawcdwatrainingtransfers where isvalid = 'true' and (trainingprogram = 'Orientation & Safety' or trainingprogram = 'Orientation & Safety Attest') """).createOrReplaceTempView("cte_rawcdwaoandstransfers")  

    traininghistory = spark.sql("""select *,p.personid as personid_new from cte_rawcdwaoandstransfers c left join person p on p.cdwaid = c.personid
    where p.personid is  not null and c.completionsrank = 1""")

    #Filtering duplicate records to injest into training history log table
    traininghistorylog = spark.sql("""select employeeid,p.personid,trainingprogram,coursename as class_name,dshscoursecode,credithours,completeddate,trainingentity,reasonfortransfer,employerstaff,createddate,filename,filedate,isvalid,'Duplicate record' as error_message from cte_rawcdwaoandstransfers c left join person p on p.cdwaid = c.personid
    where p.personid is  not null  and completionsrank > 1""") 

    #creating dynaicframes from the dataframes
    OnStransfers = DynamicFrame.fromDF(traininghistory, glueContext, "OnStransfers") 
    traininglogs = DynamicFrame.fromDF(traininghistorylog, glueContext, "traininglogs")

    #Applymapping for transfers history  									
    transfers_mapping = ApplyMapping.apply(frame = OnStransfers, mappings = [
        ("personid", "long", "personid", "long"),
        ("dshsid", "long", "dshsid", "long"),
        ("courseid", "string", "courseid", "string"),
        ("completeddate","date","completeddate","date"),
        ("coursename","string","coursename","string"),
        ("credit_hours","int","credithours","double"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("trainingprogramcode", "int", "trainingprogramcode", "long"),
        ("coursetype", "string", "coursetype", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("instructorid", "string", "instructorid", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
        ("filename", "string", "filename", "string"),
        ("filedate", "date", "filedate", "date")
                                                                
        ], transformation_ctx = "transfers_mapping")

    #Appending all valid records to training history 
    glueContext.write_dynamic_frame.from_catalog(
        frame=transfers_mapping,
        database=catalog_database,
        table_name=catalog_table_prefix+"_raw_traininghistory",
    )

    #apply apping for transfers errors	
    transfers_error_mapping = ApplyMapping.apply(frame = traininglogs, mappings = [
        ("personid", "long", "personid", "long"),
        ("dshsid", "long", "dshsid", "long"),
        ("courseid", "string", "courseid", "string"),
        ("completeddate","date","completeddate","date"),
        ("class_name","string","coursename","string"),
        ("credit_hours","int","credithours","int"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("trainingprogramcode", "int", "trainingprogramcode", "long"),
        ("coursetype", "string", "coursetype", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("instructorid", "string", "instructorid", "string"),
        ("filedate", "date", "filedate", "date"),
        ("filename", "string", "filename", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
        ("error_message", "string", "error_message", "string")
                                                                
        ], transformation_ctx = "transfers_error_mapping")   

    # Appending all error to training transfers logs
    glueContext.write_dynamic_frame.from_catalog(
        frame=transfers_error_mapping,
        database=catalog_database,
        table_name=catalog_table_prefix+"_logs_traininghistorylog",
    )
    
    maxfiledate = spark.sql(
                """select max(filedate) as filemodifieddate  from cte_rawcdwaoandstransfers """
            ).first()["filemodifieddate"]
    print(maxfiledate)

    # WRITE a record with process/execution time to logs.lastprocessed table
    lastprocessed_df = spark.createDataFrame(
        [("glue-cdwa-os-transfers-raw-to-raw-traininghistory", maxfiledate, "1")],
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
    print("Data has already processed or no new data in the source table.")
job.commit()