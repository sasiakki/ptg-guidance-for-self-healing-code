import boto3
import psycopg2
import json
import sys
from psycopg2 import Error
from awsglue.utils import getResolvedOptions

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'



# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=f'{environment_type}/b2bds/rds/system-pipelines'
)

database_secrets = json.loads(databaseresponse['SecretString'])

B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

# executing the stored procedure
def execute_sp():

    print("start connection")

    try:
        conn = psycopg2.connect(host=B2B_HOST,
                                database=B2B_DBNAME, user=B2B_USER, password=B2B_PASSWORD)

        cur = conn.cursor()
        cur.execute("begin;")
        cur.execute("CALL eligibility.sp_addto_check_person()")
        cur.execute("CALL eligibility.sp_addto_student()")
        cur.execute("CALL eligibility.sp_addto_student_status_set()")
        cur.execute("CALL eligibility.sp_addto_credential()")
        cur.execute("CALL eligibility.sp_addto_course_completion()")
        cur.execute("CALL eligibility.sp_addto_employment()")
        cur.execute("CALL eligibility.sp_addto_student_training()")
        cur.execute("commit;")
        print("Executed.")

    except:
        raise Error

    finally:
        # closing database connection.
        if conn:
            cur.close()
            conn.close()
            print("PostgreSQL connection is closed")


execute_sp()