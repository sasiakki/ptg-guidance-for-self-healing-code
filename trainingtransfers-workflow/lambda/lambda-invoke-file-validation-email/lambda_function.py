import json
import os
import sys
import logging
import boto3
from botocore.exceptions import ClientError

environment_type = os.environ['environment_type']
    
logger = logging.getLogger()
logger.setLevel(logging.INFO)

SENDER = "datastore@myseiubenefits.org"
RECIPIENTS = ["datastore@myseiubenefits.org"]

# RECIPIENTS = ["datastore@myseiubenefits.org",
#              "CDWAIntegrationsteam@consumerdirectcare.com"]
AWS_REGION = "us-west-2"
# The character encoding for the email.
CHARSET = "UTF-8"
SUBJECT = ""
BODY_TEXT = ""
BODY_HTML = ""


def lambda_handler(event, context):
    logger.info('Event: %s', event)
    print("######## Begin execution #####")
    try:
        if (event.get('filename', None) is None or event.get('filecount', None) is None):
            return {
                'statusCode': 400,
                'body': json.dumps("Input payload is not correct. Required fields filename and filecount is null.")
            }
        else:
            SendEmail(event, context)
            return {
                'statusCode': 200,
                'body': json.dumps("Email sent!")
            }
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        print("######## End execution #####")


def SendEmail(event, context):
    print("Send email")
    SUBJECT = "TP Datastore: {0} - Success".format(event["filename"])
    print(RECIPIENTS)
    print(SUBJECT)
    print("Sending email for filename: {0} with count: {1} ".format(
        event['filename'], event['filecount']))
    if (event['type'] == "Processing"):
        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("TP Datastore has received and processed the file: {0}\r\n"
                     "Number of records: {1} \r\n"
                     "Please feel free to contact us if any further information is required."
                     ).format(event['filename'], event['filecount'])
        # print(BODY_TEXT)

        # The HTML body of the email.
        BODY_HTML = """<html>
            <head></head>
            <body>
            <p>TP Datastore has received and processed the file: {0}.</p>
            <p>Number of records: {1}.</p>
            <p>Please feel free to contact us if any further information is required.</p>
            </body>
            </html>""".format(event['filename'], event['filecount'])

    elif (event['type'] == "Datavalidation"):

        BODY_TEXT = ("TP Datastore has uploaded the error file: {0} successfully to SFTP. \r\n"
                     "Number of error records: {1} \r\n"
                     "Please feel free to contact us if any further information is required."
                     ).format(event['filename'], event['filecount'])

        BODY_HTML = """<html>
        <head></head>
        <body>
        <p>TP Datastore has uploaded the error file: {0} successfully to SFTP.</p>
        <p>Number of error records: {1}.</p>
        <p>Please feel free to contact us if any further information is required.</p>
        </body>
        </html>
        """.format(event['filename'], event['filecount'])

    elif (event['type'] == "Outbound"):

        BODY_TEXT = ("TP Datastore has generated the file: {0} and successfully uploaded it to the SFTP site. \r\n"
                     "Number of records: {1} \r\n"
                     "Please feel free to contact us if any further information is required."
                     ).format(event['filename'], event['filecount'])

        BODY_HTML = """<html>
        <head></head>
        <body>
        <p>TP Datastore has generated the file: {0} and successfully uploaded it to the SFTP site.</p>
        <p>Number of records: {1}.</p>
        <p>Please feel free to contact us if any further information is required.</p>
        </body>
        </html>
        """.format(event['filename'], event['filecount'])

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': RECIPIENTS,
                # 'CcAddresses':CCRECIPIENTS,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
        # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
