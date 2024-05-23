import json
import boto3
import psycopg2
import os
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("secretsmanager")

environment_type = os.environ["environment_type"]
response1 = client.get_secret_value(
    SecretId=environment_type + "/b2bds/rds/system-pipelines"
)

database_secrets = json.loads(response1["SecretString"])

B2B_USER = database_secrets["username"]
B2B_PASSWORD = database_secrets["password"]
B2B_HOST = database_secrets["host"]
B2B_PORT = database_secrets["port"]
B2B_DBNAME = database_secrets["dbname"]


def lambda_handler(event, context):
    logger.info("Event: %s", event)
    print("######## Begin execution ########")
    # print(B2B_USER)
    try:
        # DB Connection
        db_connection = database_conn()

        if event["type"] == "Outbound":
            latestfile = db_connection.get_generatedfilecount()

            if latestfile:
                value = {"filename": latestfile[0], "filecount": latestfile[1]}
                return {
                    "statusCode": 200,
                    "body": value,
                }
            else:
                print("No records found!")
                value = {"filename": None, "filecount": None}
                return {
                    "statusCode": 200,
                    "body": value,
                    "message": "No records found!",
                }
        else:
            value = {"filename": None, "filecount": None}
            return {"statusCode": 200, "body": value, "message": "Invalid input!!"}
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        print("######## End execution ########")
        # Closing the db connection.
        db_connection.close_connection()


class database_conn:
    def __init__(self):
        self.conn = self.db_connection()

    def db_connection(self):
        try:
            conn = psycopg2.connect(
                database=B2B_DBNAME,
                user=B2B_USER,
                password=B2B_PASSWORD,
                host=B2B_HOST,
                port=B2B_PORT,
            )
            conn.autocommit = True
            logger.info("SUCCESS: Connection to RDS instance succeeded")
            return conn
        except Exception as e:
            logger.error("ERROR: Unexpected error: Could not connect to RDS instance.")
            logger.error(e)
            # sys.exit()
            raise e

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
            print("Connection Closed!!")

    def get_generatedfilecount(self):
        try:
            print("Select latest generated CDWA trainee status file record count")
            cursor = self.conn.cursor()
            SQL = """SELECT DISTINCT filename, COUNT(*)
                        FROM logs.traineestatuslogs
                    WHERE recordcreateddate::DATE = CURRENT_DATE GROUP BY filename;"""
            cursor.execute(SQL)
            row = cursor.fetchone()
            if row is None:
                print("No records found")
            else:
                print("File {0} with {1} records found.".format(row[0], row[1]))
            cursor.close()
            return row
        except Exception as e:
            raise e
