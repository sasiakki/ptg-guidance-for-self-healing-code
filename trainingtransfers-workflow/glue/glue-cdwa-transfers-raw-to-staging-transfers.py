import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from datetime import date
from pyspark.sql.functions import current_timestamp,date_format
import boto3
import json

#Default Job Arguments
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
s3bucket = s3resource.Bucket(S3_BUCKET)
s3_client = boto3.client('s3')


#creating temp view from postgres db tables
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name= catalog_table_prefix+"_raw_cdwatrainingtransfers").toDF()\
    .createOrReplaceTempView("cdwatrainingtransfers")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name= catalog_table_prefix+"_prod_transfers_trainingprogram").toDF()\
    .createOrReplaceTempView("transfertrainingprograms")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name= catalog_table_prefix+"_prod_person"
).toDF().selectExpr("*")\
    .createOrReplaceTempView("person")
    
glueContext.create_dynamic_frame.from_catalog(
   database=catalog_database,
    table_name= catalog_table_prefix+"_prod_trainingrequirement"
).toDF().selectExpr("*")\
    .createOrReplaceTempView("trainingrequirement")
    
glueContext.create_dynamic_frame.from_catalog(
   database=catalog_database,
    table_name= catalog_table_prefix+"_logs_lastprocessed"
).toDF().selectExpr("*")\
    .createOrReplaceTempView("logslastprocessed")
    


rawcdwatransfersdf = spark.sql("""SELECT * FROM cdwatrainingtransfers WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM logslastprocessed WHERE processname='glue-cdwa-transfers-raw-to-staging-transfers' AND success='1')""")

rawcdwatransfersdf.createOrReplaceTempView("cdwatrainingtransfers")
#dedup within the trainingtransfers table on personid,trainingprogram and credithours with earliest completed date and filtering the valid non-oands transfers
spark.sql("""select employeeid,personid,trainingprogram,classname,dshscoursecode,credithours,completeddate,trainingentity,'CDWATRANSFER' as trainingsource, 
reasonfortransfer,employerstaff,createddate,filedate,filename,isvalid, ROW_NUMBER() OVER ( PARTITION BY personid, trainingprogram , credithours 
ORDER BY completeddate ASC ) completionsrank from cdwatrainingtransfers where isvalid = 'true' and trainingprogram != 'Orientation & Safety' and trainingprogram != 'Orientation & Safety Attest' """).createOrReplaceTempView("cdwatrainingtransfers_dedup")

#creating dataframe for combined error file for o and s as well as non o and s
error_file = spark.sql("""select employeeid,personid,trainingprogram,classname,dshscoursecode,credithours,completeddate,trainingentity,
          reasonfortransfer,employerstaff,createddate,filename,filedate,isvalid,error_message 
          from cdwatrainingtransfers where isvalid = 'false' """ )

cdwatrainingtransfers_valid = spark.sql("""select *,p.personid as personid_new from cdwatrainingtransfers_dedup c left join person p on p.cdwaid = c.personid
where p.personid is  not null and c.completionsrank = 1""")

cdwatrainingtransfers_valid.createOrReplaceTempView("cdwatrainingtransfers_valid")


#Capturing only active training requirements
spark.sql("""
select personid,trainingprogramcode,trainingid,
                cast(trackingdate as date) as trackingdate,
                cast(duedate as date) as duedate,
                cast(duedateextension as date) as duedateextension
            from trainingrequirement where lower(status)  = 'active'
""").createOrReplaceTempView("trainingrequirement")

#Capturing person hiredate from person demographics
spark.sql(""" select cdwaid, personid, cast(hiredate as date) as hiredate from person """).createOrReplaceTempView("person")


#Maping the credithours with courseid
spark.sql("""
select ct.employeeid ,ct.personid_new,ct.classname,ct.filename,ct.employerstaff,ct.dshscoursecode,ct.completeddate,ct.trainingentity ,ct.trainingsource,ct.reasonfortransfer,tt.trainingprogramcode,tt.courseid, cast(ct.credithours as float),ct.filename,ct.filedate,ct.createddate,ct.isvalid,
case
when ct.trainingprogram = 'Basic Training 70 Hours' and cast(ct.credithours as float) = cast(tt.credithours as float) then 'Basic Training 70'
when ct.trainingprogram = 'Basic Training 30 Hours' and cast(ct.credithours as float) = cast(tt.credithours as float) then 'Basic Training 30' 
when ct.trainingprogram = 'Basic Training 9 Hours' and cast(ct.credithours as float) = cast(tt.credithours as float) then 'Basic Training 9'
when ct.trainingprogram = 'Basic Training 7 Hours' and cast(ct.credithours as float) = cast(tt.credithours as float) then 'Basic Training 7'
when ct.trainingprogram = 'Continuing Education' and cast(ct.credithours as float) between 0 and 12 then 'Continuing Education'
END as trainingprogram
from cdwatrainingtransfers_valid ct left join transfertrainingprograms tt on ct.trainingprogram  = tt.trainingprogram
""").createOrReplaceTempView("cdwatrainingtransfers_valid")


#Mapping accurate errormesage of ruled out based on errors
spark.sql(""" 
with cte_a as (select ctt.*,pt.trainingid,
                pt.trackingdate,
                pt.duedate,
                pt.duedateextension,
                pp.hiredate from cdwatrainingtransfers_valid ctt left join trainingrequirement pt  on ctt.personid_new = pt.personid and ctt.trainingprogramcode = pt.trainingprogramcode
left join person pp on ctt.personid_new = pp.personid
)select *, case when trainingprogram is null then 'Invalid transfer credit hours received'
		   when hiredate is not null and completeddate  < hiredate then 'Completion date should be greater than the hire date'
           when trainingid is null then 'No open training requirement exist'
           when trainingid is not null and completeddate NOT BETWEEN trackingdate AND coalesce(duedateextension,duedate) then 'Completion should not exceed due date or due date extension' end as error_message
           from cte_a
""").createOrReplaceTempView("transfers_validation_view")



#selecting valid data based on flags is_valid as true and transferhours is not null into staging table
stagingtransfers_df = spark.sql("select * from transfers_validation_view where error_message is null")
logtransfers_df =spark.sql("select * from transfers_validation_view where error_message is not null")

logtransfers_df.createOrReplaceTempView("logtransfers_df")

logtransfers_df_errors = spark.sql("""select employeeid,personid_new as personid,trainingprogram,classname,dshscoursecode,credithours,completeddate,trainingentity,
reasonfortransfer,employerstaff,createddate,filename,filedate,isvalid,error_message from logtransfers_df""" )


duplicate_records = spark.sql("""select employeeid,p.personid ,trainingprogram,classname,dshscoursecode,credithours,completeddate,trainingentity,reasonfortransfer,employerstaff,createddate,filename,filedate,isvalid,'Duplicate record' as error_message from cdwatrainingtransfers_dedup c left join person p on p.cdwaid = c.personid where  p.personid is  not null and completionsrank > 1""")


#creating parameters and declaring variables for error_file ingestion

today = date.today()
suffix = today.strftime("%Y-%m-%d")
filename = "Outbound/cdwa/trainingtransfers_errorlog/CDWA-O-BG-TrainingTrans-"+suffix+"-error.csv"

errorlogsfile_df = error_file.withColumnRenamed("employeeid", "Employee ID").withColumnRenamed("personid", "Person ID").withColumnRenamed("trainingprogram", "Training Program").withColumnRenamed("classname", "Class Name").withColumnRenamed("dshscoursecode", "DSHS Course Code").withColumnRenamed("credithours", "Credit Hours").withColumnRenamed("completeddate", "Completed Date").withColumnRenamed("trainingentity", "Training Entity").withColumnRenamed("reasonfortransfer", "Reason for Transfer").withColumnRenamed("employerstaff", "EmployerStaff").withColumnRenamed("createddate", "CreatedDate").withColumnRenamed("isvalid", "IsValid").withColumn("modifieddate", date_format("filedate", "yyyy-MM-dd'T'HH:mm:ss")).withColumn("dateuploaded", date_format(current_timestamp(), "yyyy-MM-dd'T'HH:mm:ss")).withColumnRenamed("error_message", "Error Message")

#Getting the dataframe columns into order
columns_order = ['Employee ID','Person ID', 'Training Program', 'Class Name','DSHS Course Code', 'Credit Hours', 'Completed Date', 'Training Entity', 'Reason for Transfer', 'EmployerStaff', 'CreatedDate', 'filename', 'dateuploaded', 'modifieddate', 'IsValid', 'Error Message']

errorlogsfile_df= errorlogsfile_df[columns_order]


#ingesting data into error file
if errorlogsfile_df.count() != 0 :
    error_df = errorlogsfile_df.toPandas()
    error_df.to_csv("s3://"+S3_BUCKET + "/" +filename,header = True, index=None, sep=',', encoding = 'utf-8', doublequote = True)

validtransferstostaging = DynamicFrame.fromDF(stagingtransfers_df, glueContext, "validtransferstostaging") 

#combining all the dataframes and creating a df to ingest ino logs table
trainingtransferslogs = (duplicate_records).unionByName(logtransfers_df_errors)

trainingtransferslogs_df = DynamicFrame.fromDF(trainingtransferslogs, glueContext, "trainingtransferslogs_df")

# Script generated for node ApplyMapping  for valid transfers
validtransfers_targetmapping = ApplyMapping.apply(
    frame=validtransferstostaging,
    mappings=[
       ("employeeid", "long", "employeeid", "bigint"),
        ("personid_new", "long", "personid", "bigint"),
        ("trainingprogram", "string", "trainingprogram", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("classname", "string", "classname", "string"),
        ("dshscoursecode", "string", "dshscoursecode", "string"),
        ("credithours", "float", "transferhours", "double"),
        ("completeddate", "date", "completeddate", "date"),
        ("trainingsource", "string", "transfersource", "string"),
        ("reasonfortransfer", "string", "reasonfortransfer", "string"),
        ("filename", "string", "filename", "string"),
        ("courseid","string","courseid","string")
    ]
)

#Appending all valid records to staging training transfers 
glueContext.write_dynamic_frame.from_catalog(frame = validtransfers_targetmapping, 
                                             database=catalog_database,
                                             table_name= catalog_table_prefix+"_staging_trainingtransfers")


#apply apping for transfers errors	
transferslogs_error_mapping = ApplyMapping.apply(frame = trainingtransferslogs_df,         
            mappings=[
            ("employeeid", "long", "employeeid", "bigint"),
            ("personid", "bigint", "personid", "bigint"),
            ("trainingprogram", "string", "trainingprogram", "string"),
            ("classname", "string", "classname", "string"),
            ("dshscoursecode", "string", "dshscoursecode", "string"),
            ("credithours", "string", "credithours", "string"),
            ("completeddate", "date", "completeddate", "date"),
            ("trainingentity", "string", "trainingentity", "string"),
            ("reasonfortransfer", "string", "reasonfortransfer", "string"),
            ("employerstaff", "string", "employerstaff", "string"),
            ("createddate", "date", "createddate", "date"),
            ("filedate", "date", "filedate", "date"),
            ("filename", "string", "filename", "string"),
            ("isvalid", "boolean", "isvalid", "boolean"),
            ("error_message", "string", "error_message", "string")
        ], transformation_ctx = "transferslogs_error_mapping")   


# Appending all error to training transfers logs
glueContext.write_dynamic_frame.from_catalog(
    frame=transferslogs_error_mapping,
    database=catalog_database,
    table_name=catalog_table_prefix+"_logs_trainingtransferslogs",
)

maxfiledate = spark.sql(
            """select max(filedate) as filemodifieddate  from cdwatrainingtransfers_dedup """
        ).first()["filemodifieddate"]
print(maxfiledate)
# Used the max_filedate instead of datetime.now() as the lastprocesseddate based on B2BDS-1532's feedback
# WRITE a record with process/execution time to logs.lastprocessed table
lastprocessed_df = spark.createDataFrame(
    [("glue-cdwa-transfers-raw-to-staging-transfers", maxfiledate, "1")],
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
job.commit()