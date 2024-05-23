import boto3
import psycopg2
import json
import sys
import pandas as pd
import csv
from awsglue.utils import getResolvedOptions
from datetime import datetime
today = datetime.now()
suffix = today.strftime("%m_%d_%Y")

args_account = getResolvedOptions(sys.argv, ["account_number", "environment_type"])
environment_type = args_account['environment_type']
aws_account = args_account['account_number']

if environment_type == 'prod':
    bg_learning_s3_bucket_name = 'seiu-learning-center'
elif environment_type == 'stage':
    bg_learning_s3_bucket_name = 'stage-seiu-learning-center'
else:
	bg_learning_s3_bucket_name = 'bg-learning-center'

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=environment_type + '/b2bds/rds/system-pipelines'
)

database_secrets = json.loads(databaseresponse['SecretString'])

B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

s3 = boto3.resource('s3')
bucket = s3.Bucket(''+bg_learning_s3_bucket_name+'')
objects = list(s3.Bucket(''+bg_learning_s3_bucket_name+'').objects.filter(Prefix='quarantine/outbound/forprocessing/'))

conn = psycopg2.connect(database=B2B_DBNAME, user=B2B_USER, password=B2B_PASSWORD, host=B2B_HOST,port=5432)
conn.autocommit = True

for obj in bucket.objects.filter(Prefix="quarantine/outbound/forprocessing/"):
    if obj.key.endswith('csv'):
        path="s3://"+bg_learning_s3_bucket_name+"/"+obj.key 
        print(path)
        df= pd.read_csv(path,usecols =['person_unique_id','approval_status','personid','firstname','lastname','ssn','dob','middlename'])
        df['personid'] = df['personid'].fillna(0).astype(int)
        df['person_unique_id'] = df['person_unique_id'].astype(int)
        df['approval_status'] = df['approval_status'].astype(str)
        df['firstname'] = df['firstname'].astype(str)
        df['lastname'] = df['lastname'].astype(str)
        df['ssn'] = df['ssn'].astype(str).replace('\.0$', '', regex=True)
        df['dob'] = df['dob'].astype(str)
        df['middlename'] = df['middlename'].astype(str)
        # Getting create value 
        dfcreate=df.where(df.approval_status=='create')
        dfcreate=dfcreate.dropna()
        dfcreate['person_unique_id'] = dfcreate['person_unique_id'].astype(int)
        dfcreate['firstname'] = dfcreate['firstname'].astype(str)
        dfcreate['lastname'] = dfcreate['lastname'].astype(str)
        dfcreate['ssn'] = dfcreate['ssn'].astype(str).replace('\.0$', '', regex=True)
        dfcreate['dob'] = dfcreate['dob'].astype(str)
        dfcreate['middlename'] = dfcreate['middlename'].astype(str)
        
        # Getting update value 
        dfupdate=df.where(df.approval_status=='update')
        dfupdate=dfupdate.dropna()
        dfupdate['personid'] = dfupdate['personid'].astype(int)
        dfupdate['person_unique_id'] = dfupdate['person_unique_id'].astype(int)
        dfupdate['firstname'] = dfupdate['firstname'].astype(str)
        dfupdate['lastname'] = dfupdate['lastname'].astype(str)
        dfupdate['ssn'] = dfupdate['ssn'].astype(str).replace('\.0$', '', regex=True)
        dfupdate['dob'] = dfupdate['dob'].astype(str)
        dfupdate['middlename'] = dfupdate['middlename'].astype(str)


        #Updating staging.personquarantine records with approval_status=='update'
        cursor = conn.cursor()
        for index, row in dfupdate.iterrows():
            SQL1 = """UPDATE staging.personquarantine p 
            SET approval_status = '{0}', personid = '{1}',firstname = COALESCE(NULLIF('{3}', 'nan'), firstname),lastname = COALESCE(NULLIF('{4}', 'nan'), lastname),ssn = COALESCE(NULLIF('{5}', 'nan'), ssn),dob = COALESCE(NULLIF('{6}', 'nan'), dob),middlename = COALESCE(NULLIF('{7}', 'nan'), middlename),recordmodifieddate = current_timestamp WHERE p.person_unique_id ='{2}'""".format(row['approval_status'],row['personid'],row['person_unique_id'],row['firstname'],row['lastname'],row['ssn'],row['dob'],row['middlename'])
            cursor.execute(SQL1)
        
        #Updating staging.personquarantine records with approval_status=='create'
        cursor = conn.cursor()
        for index, row in dfcreate.iterrows():
            SQL2 = """UPDATE staging.personquarantine p 
            SET approval_status = '{0}',firstname = COALESCE(NULLIF('{2}', 'nan'), firstname),lastname = COALESCE(NULLIF('{3}', 'nan'), lastname),ssn = COALESCE(NULLIF('{4}', 'nan'), ssn),dob = COALESCE(NULLIF('{5}', 'nan'), dob),middlename = COALESCE(NULLIF('{6}', 'nan'), middlename), recordmodifieddate = current_timestamp 
            WHERE p.person_unique_id ='{1}'""".format(row['approval_status'],row['person_unique_id'],row['firstname'],row['lastname'],row['ssn'],row['dob'],row['middlename'])
            cursor.execute(SQL2)
        
        #Exporting to S3 
        pathexport = "s3://"+bg_learning_s3_bucket_name+"/quarantine/outbound/processed/Quarantined-Persons-Export-"+suffix+".csv"
        dfexport = pd.read_sql('select * from staging.personquarantine', con=conn)
        dfexport.to_csv(pathexport,header=True, index=None, sep=',',encoding='utf-8-sig',quoting=csv.QUOTE_ALL)

        ##Delete files from processing folder
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(''+bg_learning_s3_bucket_name+'')
        objects = bucket.objects.filter(Prefix = 'quarantine/outbound/forprocessing/')
        objects_to_delete = [{'Key': o.key} for o in objects if o.key.endswith('.csv')]
        if len(objects_to_delete):
            s3_resource.meta.client.delete_objects(Bucket=''+bg_learning_s3_bucket_name+'', Delete={'Objects': objects_to_delete})


print("Insert an entry into the log table")
cursor = conn.cursor()
SQL3 = """INSERT INTO logs.lastprocessed(processname, lastprocesseddate, success)
VALUES ('glue-approve-personquarantine-records',current_timestamp, '1');"""
cursor.execute(SQL3)
print("Logs Inserted Successfully")