import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col
import pandas as pd
from pyspark.sql.functions import *
from datetime import datetime
import pandas 
import boto3
import json



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

#Capturing lastprocessed datetime from logs.lastprocessed
## B2BDS-1718: Delta Processing: DS to Salesforce (Employment Relationships & Credentials)
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, 
    table_name=catalog_table_prefix+"_logs_lastprocessed"
 ).toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")
    
### Get data 
datasource9 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_prod_employmentrelationship", transformation_ctx = "datasource9")

## convert to dataframe:
employmentrelationshipdf = datasource9.toDF()

spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

date_cols = ["authstart", "authend", "trackingdate", "terminationdate"]

for column in date_cols:
    employmentrelationshipdf = employmentrelationshipdf.withColumn(column, 
        when(col(column).contains("T"), 
             to_date(from_unixtime(unix_timestamp(col(column), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")), "yyyy-MM-dd"))
        .otherwise(to_date(col(column), "yyyy-MM-dd")))

#employmentrelationshipdf = employmentrelationshipdf.withColumn("hire_date", to_date(employmentrelationshipdf["hiredate"]).isoformat())

employmentrelationshipdf = employmentrelationshipdf.withColumn("hire_date", to_date(col("hiredate"),"%Y-%m-%dT%H:%M:%S.%fZ"))


### convert to Temp View
employmentrelationshipdf.createOrReplaceTempView("employmentrelationship")




### selct required columns
employmentrelationshipdf = spark.sql("SELECT relationshipid as RelationshipID, cast(personid as string) as PersonID, cast(employeeid as integer) as EmployeeID, cast(employerid as integer) as EmployerID, cast(branchid as integer) as BranchID, workercategory as WorkerCategory, categorycode as CategoryCode, cast(hire_date as string) as HireDate, cast(authstart as string) as AuthStart, cast(authend as string) as AuthEnd, empstatus as EmpStatus, cast(terminationdate as string) as TerminationDate, cast(trackingdate as string) as TrackingDate, isoverride as IsOverride, isignored as IsIgnored,role as Role, sfngrecordid as SFNGRecordID, source as SourceKey, recordmodifieddate, recordcreateddate FROM employmentrelationship where recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-sf-outbound-employmentrelationship' AND success='1') and personid is not null")

Eventheaderdf = spark.sql("select 'bg.seiu775.datastore' as ChangeOrigin, relationshipid as DatastoreId,case when sfngrecordid is not null then 'UPDATE' else 'CREATE' end as ChangeType,'' as RecordID, sfngrecordid as SalesforceId, 'Employment' as EntityName from employmentrelationship where recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-sf-outbound-employmentrelationship' AND success='1') and personid is not null")


#employmentrelationshipdf.show(truncate = False)
#print("Count of records to be sent to SF")
#print(employmentrelationshipdf.count())

#######################################################
if ( employmentrelationshipdf.count() > 0 ):
    ## convert to pandas
    employmentrelationshipdf = employmentrelationshipdf.toPandas()
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
    
    
        
    for i in range(0,employmentrelationshipdf.shape[0]):
        row_s=employmentrelationshipdf.iloc[i]
        row_h=Eventheaderdf.iloc[i]
        row_s=row_s.to_dict()
        row_h = row_h.to_dict()
        #temp ={}
        #temp = header_json
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
    logs_data = [[ max_filedate, "glue-sf-outbound-employmentrelationship", "1" ]] 		 
    logs_columns = ['lastprocesseddate', 'processname','success'] 		 
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
    mode = 'append'  		 
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)

job.commit()