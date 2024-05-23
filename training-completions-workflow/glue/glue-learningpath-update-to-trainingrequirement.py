import sys
import pandas as pd
import psycopg2
from psycopg2 import sql
import os
import boto3
import json
from awsglue.utils import getResolvedOptions


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
    SecretId= environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId = environment_type+'/b2bds/rds/system-pipelines'
)
database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

s3resource = boto3.resource('s3')

class b2b_conn():
    def __init__(self):
        self.conn = self.sqldb_connection()

    def sqldb_connection(self):
        username = B2B_USER
        password = B2B_PASSWORD
        host_name = B2B_HOST
        port = B2B_PORT
        db_name = B2B_DBNAME
        
        conn = psycopg2.connect(database=db_name, user=username, password=password, 
                                  host=host_name,port=port)
        conn.autocommit = True
        return conn
        
    def connect(self):
        cur= self.conn.cursor()
        
       
        try:
            
            cur.execute("""
            UPDATE prod.transcript p
            SET trainingid = staging.learningpath_updates.trainingid, recordmodifieddate = current_timestamp
            from staging.learningpath_updates 
            WHERE p.transcriptid = staging.learningpath_updates.transcriptid ;
            """)
            cur.execute("""UPDATE prod.trainingrequirement 
            SET learningpath = staging.learningpath_updates.learningpath,recordmodifieddate = current_timestamp,
            earnedhours = staging.learningpath_updates.earnedhours,
            status = staging.learningpath_updates.status
            FROM staging.learningpath_updates
            WHERE staging.learningpath_updates.trainingid = prod.trainingrequirement.trainingid and staging.learningpath_updates.trainingid is not null
            """)
            self.conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        
        finally:
            if self.conn is not None:
                self.conn.close()
                print('Database connection closed.')





if __name__ == '__main__':
    dbO = b2b_conn()
    dbO.connect();