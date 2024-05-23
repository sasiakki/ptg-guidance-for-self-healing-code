import json
import boto3
import psycopg2
import os


def lambda_handler(event, context):
       
    environment_type = os.environ['environment_type']

    # Retrieve secrets from AWS Secrets Manager.
    secrets_manager_client = boto3.client('secretsmanager')
    try:
        database_secrets_response = secrets_manager_client.get_secret_value(
            SecretId="{}/b2bds/rds/system-pipelines".format(environment_type))
    except Exception as e:
        print(f"Failed to retrieve Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to retrieve Secrets Manager secret.','result': False}
    # Load secret string response into JSON.
    try:
        database_secrets = json.loads(database_secrets_response['SecretString'])
    except Exception as e:
        print(f"Failed to parse Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to parse Secrets Manager secret.','result': False}
    # Get SFTP detaiils from secrets.
    try:
        B2B_USER = database_secrets['username']
        B2B_PASSWORD = database_secrets['password']
        B2B_HOST = database_secrets['host']
        B2B_PORT = database_secrets['port']
        B2B_NAME = database_secrets['dbname']
    except Exception as e:
        print(f"Failed to get database information from Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to get database information from Secrets Manager secret.','result': False}
    try:
        #DB Connection
        db_connection = B2B_conn(B2B_USER,B2B_PASSWORD,B2B_HOST,B2B_PORT,B2B_NAME)
        
        #print(event)
        
        insert_processed_files = event['insert_processed_file']
       
        
        for insert_processed_file in insert_processed_files:
            db_connection.write_processed_files(insert_processed_file)
            
        
        event.update({'statusCode': 200, 'result': True, 'insert_processed_files':insert_processed_files} )
        return  event 

    except Exception as e:
        print(f"Failed to connect to database based on information from Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to connect to database based on information from Secrets Manager secret.','result': False}
    finally:
        db_connection.close_connection()


class B2B_conn():
    def __init__(self,username,password,host_name,port,db_name):
        self.username = username
        self.password = password
        self.host_name = host_name
        self.port = port
        self.db_name = db_name
        self.conn = self.sqldb_connection()
        

    def sqldb_connection(self):
        conn = psycopg2.connect(database=self.db_name, user=self.username, password=self.password, 
                                  host=self.host_name,port=self.port)
        conn.autocommit = True
        return conn

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
        print("Connection Closed!!")

    def write_processed_files(self, file_meta_data):
        """This function appends processed files into the Data Exachange DB. All meta data should be derived prior to passing into this function.

        INPUT:
            [(FileName, recordcreateddate, recordmodifieddate, Length of file, MemorySize, Category, filedate), ...]
        """
        cursor = self.conn.cursor()
        
        SQL = """INSERT INTO logs.sftpfilelog (filename, processeddate, numberofrows, filesize, filecategory)
            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(file_meta_data['filename'], file_meta_data['processeddate'], file_meta_data['numberofrows'], file_meta_data['filesize'], file_meta_data['filecategory'])
        
        
        cursor.execute(SQL)
        self.conn.commit()
        print("INSERT SUCCESSFUL, FILE INSERTED: " + file_meta_data['filename'])