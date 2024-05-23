import json, sys
import boto3
import psycopg2
from psycopg2 import Error
from awsglue.utils import getResolvedOptions

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

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



if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'
    

# executing the stored procedure 
def execute_sp():
    print("start connection")
    try:
        conn = psycopg2.connect(host=B2B_HOST,
                                database=B2B_DBNAME, user=B2B_USER, password=B2B_PASSWORD)
        cur = conn.cursor()
        cur.execute("begin;")
        cur.execute("CALL staging.sp_benefitscontinuation_duedateupdate_trainingrequirement()")
        cur.execute("commit;")
        print("Excuted SP staging.sp_benefitscontinuation_duedateupdate_trainingrequirement fine")
        print("connected")
    except:
        raise Error
    finally:	
        #closing database connections.	
        if conn:	
            cur.close()	
            conn.close()	
            print("PostgreSQL connection is closed")	


execute_sp()

