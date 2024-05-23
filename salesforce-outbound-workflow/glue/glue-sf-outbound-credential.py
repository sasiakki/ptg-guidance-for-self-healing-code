import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
import pandas as pd
from datetime import datetime
import pandas 
import boto3
import json


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
   

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

#Capturing lastprocessed datetime from logs.lastprocessed
## B2BDS-1718: Access the lastprocessed log table and create a DF for Delta Detection purpose
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, 
    table_name=catalog_table_prefix+"_logs_lastprocessed"
 ).toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")

### Get data 
credentialdf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_prod_credential").toDF()

# ###B2BDS-1718 Get Person DF, to differentiate the person information to outbound is CREATE/UPDATE
# persondf = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_prod_person").toDF()

credentialsfid = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_prod_credentialsfid").toDF()



for col_name in ["firstissuancedate","lastissuancedate","expirationdate"]:
    credentialdf = credentialdf.withColumn(col_name, date_format(unix_timestamp(col_name , "mm/dd/yyyy").cast("timestamp"),"yyyy/mm/dd"))
    credentialdf = credentialdf.withColumn(col_name, regexp_replace(col_name, '/', '-'))
credentialdf.show()



### convert to Temp View
credentialdf.createOrReplaceTempView("credential")
credentialsfid.createOrReplaceTempView("credentialsfid")
credentialdf = spark.sql("select credentialnumber as CredentialNumber, cast(personid as string) as PersonID, \
primarycredential as PrimaryCredential, credentialtype as Type, cast(firstissuancedate as string) as FirstIssuance, \
cast(lastissuancedate as string) as LastIssuance, cast(expirationdate as string) as Expiration, \
credentialstatus as CredentialStatus, recordmodifieddate, recordcreateddate \
from credential where personid is not null AND recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-sf-outbound-credential' AND success='1')")

credentialdf.createOrReplaceTempView("credentialdf")

Eventheaderdf = spark.sql("""select 'bg.seiu775.datastore' as ChangeOrigin, c.CredentialNumber as DatastoreId,
case when d.SFCredentialID is not null then 'UPDATE' else 'CREATE' end as ChangeType, ' ' as RecordID, 'Credential__c' as EntityName from credentialdf c 
left join credentialsfid d on c.CredentialNumber = d.credentialnumber 
where c.PersonID is not null AND c.recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed 
WHERE processname='glue-sf-outbound-credential' AND success='1')""")

credentialdf.show(truncate = False)
print("Count of records to be sent to SF")
print(credentialdf.count())

#######################################################
if ( credentialdf.count() > 0 ):
    ## convert to pandas
    credentialdf = credentialdf.toPandas()
    Eventheaderdf=Eventheaderdf.toPandas()
    
    row_s=[]
    row_h =[]
    
    footer_json ={"schemaId": "Jjksdah-sajkhd",
          "id": "2d123se-f3a4-43d6-a4b8-xxxxxxx"}
          
    client = boto3.client('events', region_name='us-west-2')
    print("sucessfully invoked")
    response = client.list_rules(
        EventBusName=f'arn:aws:events:us-west-2:{aws_account}:event-bus/default',
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
    
    print("Insert an entry into the log table")
    url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
    properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
    max_filedate = datetime.now()
    #max_filedate = raw_cs_cornerstone_completion_df.max()['filedate']
    logs_data = [[ max_filedate, "glue-sf-outbound-credential", "1" ]] 		 
    logs_columns = ['lastprocesseddate', 'processname','success'] 		 
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
    mode = 'append'  		 
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)


job.commit()