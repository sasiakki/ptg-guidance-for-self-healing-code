import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import pandas as pd
from awsglue.job import Job
import pandas 
import boto3




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
datasource4 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_prod_employer", transformation_ctx = "datasource4")


## convert to dataframe:
employerdf = datasource4.toDF()
employerdf.show()
print("Count of records to be sent to SF")
print(employerdf.count())
### convert to Temp View

employerdf.createOrReplaceTempView("employer")




### selct required columns

employerdf = spark.sql("select employerid as EmployerID, employername as EmployerName, type as Type, address as Address, recordmodifieddate, recordcreateddate from employer where cast(recordmodifieddate as date) = cast(current_date as date)")

Eventheaderdf = spark.sql("select 'bg.seiu775.datastore' as ChangeOrigin, employerid as DatastoreId, \
case when recordmodifieddate <> recordcreateddate then 'UPDATE' else 'CREATE' end as ChangeType, \
'' as RecordID,  'Account' as EntityName from employer where cast(recordmodifieddate as date) = cast(current_date as date)")


employerdf.show(truncate = False)


## convert to pandas

employerdf = employerdf.toPandas()
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


    
for i in range(0,employerdf.shape[0]):
    row_s=employerdf.iloc[i]
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
    #payload_c = json.dumps(payload_c)
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




job.commit()