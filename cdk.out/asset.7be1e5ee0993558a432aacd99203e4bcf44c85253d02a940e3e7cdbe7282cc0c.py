import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col
from pyspark.sql.functions import *
import pandas as pd
from awsglue.job import Job
import pandas 
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

    
### Get data 
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_prod_person", transformation_ctx = "datasource0")
datasource1 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource1")

## convert to dataframe:
persondf = datasource0.toDF()
logsdf=datasource1.toDF()


persondf = persondf.withColumn("hire_date", to_date(col("hiredate"),"y-%M-%d"))
persondf = persondf.withColumn("tracking_date", to_date(col("trackingdate"),"y-%M-%d"))

persondf.show()
### convert to Temp View
persondf.createOrReplaceTempView("person")
logsdf.createOrReplaceTempView("lastprocessed")


### selct required columns
lastprocesseddate=spark.sql("""select case 
                    when max(lastprocesseddate) is null then (current_date -1)
                    else max(lastprocesseddate)
                    end as maxprocessdate
                    from lastprocessed
                    where processname= 'glue-sf-outbound-person'
                    and success= '1'""")
maxprocesseddate= lastprocesseddate.select(first(lastprocesseddate.columns[0])).collect()[0][0]
persondf =spark.sql(f"""select sfcontactid, cast(personid as string) as personID, firstname as FirstName, lastname as LastName, 
middlename as MiddleName, email1 as Email1, email2 as Email2, dob as DOB, ssn as SSN, homephone as HomePhone, mobilephone as MobilePhone, 
language as Language, 
mailingstreet1 as MailingStreet1, mailingstreet2 as MailingStreet2, 
mailingcity as MailingCity, mailingstate as MailingState, 
mailingzip as MailingZip, mailingcountry as MailingCountry, 
trainingstatus as TrainingStatus,
exempt as Exempt,
status as EmpStatus, 
cast(hire_date as string) as HireDate,
type as Type, 
workercategory as WorkerCategory,
categorycode as CategoryCode,
cast(tracking_date as string) as TrackingDate,
iscarinaeligible as isCarinaEligible,
ahcas_eligible as AHCASEligible, 
matched_sourcekeys as SourceKey from person where recordmodifieddate > '{maxprocesseddate}' and personid is not null""")


Eventheaderdf = spark.sql(f"""select 'bg.seiu775.datastore' as ChangeOrigin, 
case when sfcontactid is not null then 'UPDATE' else 'CREATE' end as ChangeType, 
sfcontactid as RecordID, 'Contact' as EntityName, personid as DatastoreId, 
sfcontactid as SalesforceId from person where recordmodifieddate > '{maxprocesseddate}' and personid is not null""")


## convert to pandas

persondf = persondf.toPandas()
Eventheaderdf=Eventheaderdf.toPandas()

row_s=[]
row_h =[]

    
footer_json ={"schemaId": "Jjksdah-sajkhd",
      "id": "2d123se-f3a4-43d6-a4b8-xxxxxxx"}
      
#json_string  = '{"Payload__c":"{\"LastName\":\"""\"}"}'

client = boto3.client('events', region_name='us-west-2')
print("sucessfully invoked")
response = client.list_rules(
    EventBusName=f'arn:aws:events:us-west-2:{aws_account}:event-bus/default',
    Limit=10
)
print("List of rules:",response)


    
for i in range(0,persondf.shape[0]):
    row_s=persondf.iloc[i]
    row_h=Eventheaderdf.iloc[i]
    row_s=row_s.to_dict()
    row_h = row_h.to_dict()
    ds = {}
    payload = {}
    #event = {}
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

    payload=pandas.Series(payload)
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

    [('glue-sf-outbound-person', log_time, "1")], schema=["processname", "lastprocesseddate", "success"])

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