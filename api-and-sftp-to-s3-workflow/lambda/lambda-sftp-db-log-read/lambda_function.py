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
        latestprocesseddate = db_connection.get_processed(event['category'])
        event.update({'statusCode': 200, 'result': True, 'latestprocesseddate':latestprocesseddate} )
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
    
        # Function to close the connection. 
    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
        print("Connection Closed!!")


    def get_processed(self,category):
        """ Get latest processed date from the processed files
        """
        print("PULLING LATEST PROCESSEDDATE FROM LOG TABLE")
        cursor = self.conn.cursor()
        
        SQL = """select to_char(processeddate,'YYYY-MM-DD 23:59:59') as processeddate from logs.sftpfilelog where filecategory = '{0}' order by processeddate desc limit 1""".format(category)
        cursor.execute(SQL)
        row = cursor.fetchone()
        if row == None: 
            latestprocesseddate = '0' 
        else: 
            latestprocesseddate = row[0]
        cursor.close()
        
        return latestprocesseddate