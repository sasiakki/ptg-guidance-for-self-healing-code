import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
import pandas as pd
import json
import boto3
from datetime import datetime

log_time=datetime.now()

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

args_account = getResolvedOptions(sys.argv, ["account_number", "environment_type"])	
aws_account = args_account['account_number']	
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


# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/rds/system-pipelines'
)
database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']


s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')
#sourcepath = "s3://"+S3_BUCKET+"/Inbound/raw/Learningpath/"  


# Accessing data from rhe catalog tables and creating dataframe from dynamic frame
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_prod_credential",
).toDF().createOrReplaceTempView("prod_credential")

glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_dohclassified",
).toDF().createOrReplaceTempView("prod_dohclassfied")

glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_dohcompleted",
).toDF().createOrReplaceTempView("prod_dohcompleted")
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource0")

## convert to dataframe:
logsdf=datasource0.toDF()

logsdf.createOrReplaceTempView("lastprocessed")
#selecting lastprocessed date

lastprocesseddate=spark.sql("""select case 
                    when max(lastprocesseddate) is null then (current_date -1)
                    else max(lastprocesseddate)
                    end as maxprocessdate
                    from lastprocessed
                    where processname= 'glue-sf-benefits-certification-fund'
                    and success= '1'""")
maxprocesseddate= lastprocesseddate.select(first(lastprocesseddate.columns[0])).collect()[0][0]
#selecting the required columns 
cred = spark.sql("""select personid,dohcertduedate,providernamedoh,examscheduleddate,examscheduledsitename,credentialnumber,recordmodifieddate from prod_credential where personid is not null""")
cred.createOrReplaceTempView("credentials")

classified = spark.sql(f"""select credentialnumber,classifieddate from prod_dohclassfied 
where recordmodifieddate > '{maxprocesseddate}' order by recordmodifieddate""")
classified.createOrReplaceTempView("dohclassfied")

completed = spark.sql(f"""select credentialnumber,completeddate from prod_dohcompleted 
where recordmodifieddate > '{maxprocesseddate}' order by recordmodifieddate""")
completed.createOrReplaceTempView("dohcompleted")

cred_df = spark.sql("""select Personid,dohcertduedate,providernamedoh,examscheduleddate,examscheduledsitename,c.credentialnumber,recordmodifieddate,completeddate,classifieddate from credentials c join dohclassfied d on c.credentialnumber = d.credentialnumber
join dohcompleted e on e.credentialnumber = c.credentialnumber """)


cred_df.createOrReplaceTempView("credinals_df")


headerdf = spark.sql("""select 'bg.seiu775.datastore' as ChangeOrigin, Personid as DatastoreId, 'UPDATE' as ChangeType, 
'' as RecordID, 'Certification_Benefit_Fund__c' as EntityName from credinals_df """)

#Converting dataframe to pandas df
credentialdf = cred_df.toPandas()
Eventheaderdf=headerdf.toPandas()

row_s=[]
row_h =[]

    
footer_json ={"schemaId": "Jjksdah-sajkhd",
      "id": "2d123se-f3a4-43d6-a4b8-xxxxxxx"}
      

client = boto3.client('events', region_name='us-west-2')
print("sucessfully invoked")
response = client.list_rules(
    EventBusName='default',
    Limit=10
)
print("List of rules:",response)


    
for i in range(0,credentialdf.shape[0]):
    row_s=credentialdf.iloc[i]
    row_h=Eventheaderdf.iloc[i]
    row_s=row_s.to_dict()
    row_h = row_h.to_dict()
    ds = {}
    payload = {}
    foot={}
    key = "EventHeader"
    value = row_h
    ds[key] = value
    ds.update(row_s)
    
    ds  =pd.Series(ds)

    key = "payload"
    value = ds
    payload[key] = value
    print("printing payload")
    payload=pd.Series(payload)
    payload = payload.to_json(orient = 'index',indent =1,date_format='iso')
    print(payload)

    response = client.put_events(
    Entries=[
        {
            'Source': 'bg.seiu775.datastore',
            'DetailType': 'entitychangeevent',
            'Detail': payload,
            'EventBusName': f'arn:aws:events:us-west-2:{aws_account}:event-bus/default'
        }
    ])
    print("Response from put events")
    print(response)
# WRITE a record with process/execution time to logs.lastprocessed table

lastprocessed_df = spark.createDataFrame(

    [('glue-sf-benefits-certification-fund', log_time, "1")], schema=["processname", "lastprocesseddate", "success"])

# Create Dynamic Frame to log lastprocessed table

lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext, "lastprocessed_cdf")

lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[

    ("processname", "string", "processname", "string"),

    ("lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"),

    ("success", "string", "success", "string")])

lastprocessed_cdf_applymapping.show()

# Write to PostgreSQL logs.lastprocessed table of the success

PostgreSQLtable_node = glueContext.write_dynamic_frame.from_catalog(

    frame=lastprocessed_cdf_applymapping,

    database=catalog_database,

    table_name=catalog_table_prefix+"_logs_lastprocessed",

    transformation_ctx="PostgreSQLtable_node",

)

job.commit()