import json
import boto3
import psycopg2
import os
import sys
import logging

environment_type = os.environ['environment_type']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('secretsmanager')

response1 = client.get_secret_value(
    SecretId=environment_type + '/b2bds/rds/system-pipelines'
)

database_secrets = json.loads(response1['SecretString'])

B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']


def lambda_handler(event, context):
    logger.info('Event: %s', event)
    print("######## Begin execution #####")
    # print(B2B_USER)
    try:
        # DB Connection
        db_connection = database_conn()

        if (event['type'] == "Processing"):
            latestfile = db_connection.get_processedfilecount()

            if latestfile:
                value = {
                    "filename": latestfile[0],
                    "filecount": latestfile[1]
                }
                return {
                    'statusCode': 200,
                    'body': value,
                }
            else:
                print("No records found")
                value = {
                    "filename": None,
                    "filecount": None
                }
                return {
                    'statusCode': 200,
                    'body': value,
                    'message': 'No records found'
                }

        elif (event['type'] == "Datavalidation"):
            errorfile = db_connection.get_errorfilecount()

            if errorfile:
                value = {
                    "filename": errorfile[0],
                    "filecount": errorfile[1]
                }
                return {
                    'statusCode': 200,
                    'body': value
                }
            else:
                value = {
                    "filename": None,
                    "filecount": None
                }
                print("No records found")
                return {
                    'statusCode': 200,
                    'body': value,
                    'message': 'No records found'
                }
        else:
            value = {
                "filename": None,
                "filecount": None
            }
            return {
                'statusCode': 200,
                'body': value,
                'message': 'Invalid input!!'
            }
    except Exception as e:
        logger.error(e)
        raise e
    
    finally: 
        db_connection.close_connection()


class database_conn():
    def __init__(self):
        self.conn = self.db_connection()

    def db_connection(self):
        try:
            conn = psycopg2.connect(database=B2B_DBNAME, user=B2B_USER, password=B2B_PASSWORD,
                                    host=B2B_HOST, port=B2B_PORT)
            conn.autocommit = True
            logger.info("SUCCESS: Connection to RDS instance succeeded")
            return conn
        except Exception as e:
            logger.error(
                "ERROR: Unexpected error: Could not connect to RDS instance.")
            logger.error(e)
            sys.exit()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
            logger.info("Closing RDS connection")


    def get_processedfilecount(self):
        try:
            print("Select latest processed CDWA training transfers file record count")
            cursor = self.conn.cursor()
            SQL = """with cte as(
                            SELECT filename,
                                   COUNT(*)
                            FROM raw.cdwatrainingtransfers
                            WHERE recordcreateddate::DATE = CURRENT_DATE
                            AND   filename = concat('CDWA-O-BG-TrainingTrans-',CURRENT_DATE,'.csv')
                            GROUP BY filename
                            )
                            
                            SELECT filename,
                                   SUM(COUNT) as totalcount
                            FROM cte
                            GROUP BY filename; """
            cursor.execute(SQL)
            row = cursor.fetchone()
            if row is None:
                print("No records found")
            else:
                print("File {0} with {1} records found.".format(
                    row[0], row[1]))
            cursor.close()
            return row
        except Exception as e:
            raise e
        # finally:
        #     if (self.conn):
        #         print("Closing RDS connection")
        #         self.conn.close()

    def get_errorfilecount(self):
        try:
            print("Select latest processed CDWA training transfers file error count")
            cursor = self.conn.cursor()
            SQL = """WITH cte AS
                    (
                      SELECT REPLACE(filename,'.csv','-error.csv') AS filename,
                             COUNT(*)
                      FROM raw.cdwatrainingtransfers
                      WHERE isvalid = FALSE
                      AND   recordcreateddate::DATE = CURRENT_DATE
                      AND   filename = concat('CDWA-O-BG-TrainingTrans-',CURRENT_DATE,'.csv')
                      GROUP BY filename
                    )
                    SELECT filename,
                           SUM(COUNT) AS totalcount
                    FROM cte
                    GROUP BY filename; """
            cursor.execute(SQL)
            row = cursor.fetchone()
            if row is None:
                print("No records found")
            else:
                print("File {0} with {1} records found.".format(
                    row[0], row[1]))
            cursor.close()
            return row
        except Exception as e:
            raise e
        # finally:
        #     if (self.conn):
        #         print("Closing RDS connection")
        #         self.conn.close()
