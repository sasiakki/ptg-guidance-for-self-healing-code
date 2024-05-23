
import json
import os
import boto3
import psycopg2
from psycopg2 import sql
import pandas as pd
from datetime import datetime
from pandas.api.types import is_datetime64_dtype
import re

client10 = boto3.client('secretsmanager')

response1 = client10.get_secret_value(
    SecretId='prod/b2bds/rds/system-pipelines'
)

execute_string = """"""

database_secrets = json.loads(response1['SecretString'])

B2B_USER = database_secrets['username']
B2B_PASS = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_NAME = 'b2bds'


#Function to clean the event structure and gather the columns hence create a dataframe
def event_df(event):
    print(event)
    dic = {'sfngrecordid':'','relationshipid':'','recordmodifieddate':''}
    for key, value in dic.items():
        dic['sfngrecordid'] = event['detail']['ChangeEventHeader']['recordIds'][0]
        dic['relationshipid'] = event['detail']['Relationship_Id_Sync__c'].split("_", 1)[0]
        dic['recordmodifieddate']= datetime.now().isoformat()
    print(dic)
    
    return dic
   
   
   
def lambda_handler(event, context):
    print(event)
    username = B2B_USER
    password = B2B_PASS
    host_name = B2B_HOST
    port = B2B_PORT
    db_name = B2B_NAME
    dataFrame = event_df(event)
    print(dataFrame)
    dbO = b2b_conn()
    dbO.insert_(dataFrame)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully Executed Lambda!')
    }
   
#Connecting to the database     
class b2b_conn():
    def __init__(self):
        self.conn = self.sqldb_connection()

    def sqldb_connection(self):
        username = B2B_USER
        password = B2B_PASS
        host_name = B2B_HOST
        port = B2B_PORT
        db_name = B2B_NAME
        
        conn = psycopg2.connect(database=db_name, user=username, password=password, 
                                  host=host_name,port=port)
        conn.autocommit = True
        return conn

#function to update data into the database        
    def insert_(self, df):
        relationshipid = df['relationshipid']
        print(relationshipid)
        update_fields = list(df.keys())
        print(update_fields)
        update_sql = sql.SQL("""UPDATE prod.employmentrelationship SET ({}) = ({}) WHERE relationshipid = %(relationshipid)s """).format(sql.SQL(", ").join(map(sql.Identifier, update_fields)),sql.SQL(", ").join(map(sql.Placeholder, update_fields)))
        cur = self.conn.cursor()
        try:
            cur.execute(update_sql,df)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            self.conn.rollback()
            cur.close()
            self.conn.close()
            return 1
        print("execute sql() done")
        cur.close()
        self.conn.close()
        
		
		
            
        
        
        
 

