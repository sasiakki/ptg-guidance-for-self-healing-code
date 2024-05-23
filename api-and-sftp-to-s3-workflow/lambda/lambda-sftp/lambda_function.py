import json
import paramiko
import os
import boto3
import re
from datetime import datetime
import pandas as pd

def lambda_handler(event, context):

    update_event(event=event)

    # Determine the environment type based on an environment variable
    environment_type = os.environ['environment_type']

    try:
        # Retrieve the SFTP and S3 secrets from AWS Secrets Manager
        sftp_secrets = retrieve_secrets(
            f"{environment_type}/b2bds/sftp/{event['sftp']}")
        s3_secrets = retrieve_secrets(f"{environment_type}/b2bds/s3")
    except Exception as e:
        print(f"Failed to retrieve Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to retrieve Secrets Manager secret.', 'result': False}

    # Extract SFTP connection details and S3 bucket name from the retrieved secrets
    sftp_host, sftp_port, sftp_user, sftp_password = get_sftp_details(
        sftp_secrets)
    s3_bucket_name = get_s3_bucket_name(s3_secrets)

    try:
        # Connect to the SFTP server and download files
        transport = connect_to_sftp(
            sftp_host, sftp_port, sftp_user, sftp_password)
        file_paths = download_files_from_sftp(transport, event)
        transport.close()
    except Exception as e:
        print(f"Failed to connect to or download files from SFTP: {e}")
        return {'statusCode': 500, 'error': 'Failed to connect to or download files from SFTP.', 'result': False}

    if len(file_paths) > 0:
        try:
            # Upload downloaded files to the S3 bucket and gather information about the uploaded files
            insert_processed_file = upload_to_s3(
                event, file_paths, s3_bucket_name)
            output = {'insert_processed_file': insert_processed_file,
                      'message': 'File Transfer Success',
                      'status_code': 201
                      }
        except Exception as e:
            print(f"Failed to upload files to S3: {e}")
            return {'statusCode': 500, 'error': 'Failed to upload files to S3.', 'result': False}
    else:
        print('No files to process')
        output = {'insert_processed_file': [],
                  'message': 'Successfully ran with no files',
                  'status_code': 204
                  }

    return output


def update_event(event):
    
    #event.update({'latestprocesseddate': "2023-07-17 23:59:59"})
    
    if event['category'] == 'credential':
        event.update(
            {'re_fileformat': "(01250_TPCertification_ADSAToTP_)(\\d\\d\\d\\d\\d\\d\\d\\d_\\d\\d\\d\\d\\d\\d)(.TXT)"})
        event.update({'re_datepattern': "%Y%m%d_%H%M%S"})
        event.update({'sftp': "dshs"})
        event.update({'sftpFolder': "/"})
        event.update({'s3Subfolder': "Inbound/raw/credential"})
        event.update({'fileformat': "01250_TPCertification_ADSAToTP_"})

    elif event['category'] == 'exam':
        event.update(
            {'re_fileformat': "(01250_TPExam_ADSAToTP_)(\\d\\d\\d\\d\\d\\d\\d\\d_\\d\\d\\d\\d\\d\\d)(.TXT)"})
        event.update({'re_datepattern': "%Y%m%d_%H%M%S"})
        event.update({'sftp': "dshs"})
        event.update({'sftpFolder': "/"})
        event.update({'s3Subfolder': "Inbound/raw/exam"})
        event.update({'fileformat': "01250_TPExam_ADSAToTP_"})

    elif event['category'] == 'cdwa-trainingtransfer':
        event.update(
            {'re_fileformat': "(CDWA-O-BG-TrainingTrans-)(\\d{4}-\\d{2}-\\d{2})(.csv)"})
        event.update({'re_datepattern': "%Y-%m-%d"})
        event.update({'sftp': "cdwa"})
        event.update({'sftpFolder': "/Benefits_Group/prod/From_CDWA"})
        event.update({'s3Subfolder': "Inbound/raw/cdwa/trainingtransfer"})
        event.update({'fileformat': "CDWA-O-BG-TrainingTrans"})

    elif event['category'] == 'cdwa-providerinfo':
        event.update(
            {'re_fileformat': "(CDWA-O-BG-ProviderInfo-)(\\d{4}-\\d{2}-\\d{2})(.csv)"})
        event.update({'re_datepattern': "%Y-%m-%d"})
        event.update({'sftp': "cdwa"})
        event.update({'sftpFolder': "/Benefits_Group/prod/From_CDWA"})
        event.update({'s3Subfolder': "Inbound/raw/cdwa/ProviderInfo"})
        event.update({'fileformat': "CDWA-O-BG-ProviderInfo"})


    elif event['category'] == 'doh-inbound-completed':
        event.update(
            {'re_fileformat': "(HMCC - DSHS Benefit Training Completed File )(\\d{4}_\\d{2}_\\d{2}_\\d{6})(.*)"})
        event.update({'re_datepattern': "%Y_%m_%d_%H%M%S"})
        event.update({'sftp': "doh"})
        event.update({'sftpFolder': "Reports"})
        event.update({'s3Subfolder': "Inbound/raw/doh/completed"})
        event.update(
            {'fileformat': "HMCC - DSHS Benefit Training Completed File"})

    elif event['category'] == 'doh-inbound-classified':
        event.update(
            {'re_fileformat': "(HMCC - DSHS Benefit Classified File )(\\d{4}_\\d{2}_\\d{2}_\\d{6})(.*)"})
        event.update({'re_datepattern': "%Y_%m_%d_%H%M%S"})
        event.update({'sftp': "doh"})
        event.update({'sftpFolder': "Reports"})
        event.update({'s3Subfolder': "Inbound/raw/doh/classified"})
        event.update({'fileformat': "HMCC - DSHS Benefit Classified File"})
    

def get_environment_type():
    # Retrieve the account number from an environment variable
    account_number = os.environ.get('account_number')
    # Determine the environment type based on the account number
    return 'prod' if account_number == '259367569391' else 'dev'


def retrieve_secrets(secret_id):
    # Create an AWS Secrets Manager client
    secrets_manager_client = boto3.client('secretsmanager')
    # Retrieve the secret value using the specified secret ID
    response = secrets_manager_client.get_secret_value(SecretId=secret_id)
    secret_string = response['SecretString']
    # Parse the secret string as JSON and return the result
    return json.loads(secret_string)


def get_sftp_details(sftp_secrets):
    # Extract SFTP connection details from the retrieved secrets
    return sftp_secrets['host'], sftp_secrets['port'], sftp_secrets['username'], sftp_secrets['password']


def get_s3_bucket_name(s3_secrets):
    # Extract the S3 bucket name from the retrieved secrets
    return s3_secrets['datafeeds']


def connect_to_sftp(host, port, username, password):
    # Create a Paramiko transport object and connect to the SFTP server
    transport = paramiko.Transport((host, int(port)))
    transport.connect(username=username, password=password)
    return transport


def download_files_from_sftp(transport, event):
    # Create an SFTP client from the Paramiko transport object
    if event["latestprocesseddate"] !="0" :
        sftp = paramiko.SFTPClient.from_transport(transport)
        file_paths = []
        latest_processed_date = datetime.strptime(
            event["latestprocesseddate"], '%Y-%m-%d %H:%M:%S').date()
        if 'sftpFolder' in event:
            # Change to the specified SFTP folder
            sftp.chdir(event['sftpFolder'])

        # Filter files in the SFTP directory based on the specified file format
        filtered_files = [filename for filename in sftp.listdir()
                        if event['fileformat'] in filename]
        print(
            f"Files Matching the {event['fileformat']} in directory {event['sftpFolder']}: {len(filtered_files)}")

        for filename in filtered_files:
            # Check if the filename matches the expected format using regular expressions
            ismatch = re.search(event['re_fileformat'], filename)

            if ismatch:
                incoming_file_date = datetime.strptime(
                    ismatch.group(2), event['re_datepattern']).date()
                if incoming_file_date > latest_processed_date:
                    try:
                        print(f"Get file : {filename}")
                        # Download the file to the /tmp directory
                        sftp.get(filename, '/tmp/' + filename)
                        # event['fileformat'] == 'xls':
                        if filename.lower().endswith('.xls'):
                            read_file = pd.read_excel('/tmp/'+filename)
                            filename = str(filename.split(".")[0])
                            filename  = filename+'.csv'
                            read_file.to_csv('/tmp/'+ filename, sep=',', index=None, header=True)

                        file_paths.append('/tmp/' + filename)
                    except Exception as e:
                        print(
                            f"Unable to add the file {filename} to the list of file paths: {file_paths}")
                        raise e

        sftp.close()
    return file_paths


def upload_to_s3(event, file_paths, s3_bucket_name):
    # Create an S3 client
    s3_client = boto3.client('s3')
    insert_processed_file = []

    for file_path in file_paths:
        try:
            print(
                f"Upload file: {file_path} to s3 bucket: {s3_bucket_name} subfolder: {event['s3Subfolder']}")

            # Upload the file to the specified S3 bucket and subfolder
            processing_file_key = event['s3Subfolder'] + \
                file_path.replace('/tmp', '')
            s3_client.upload_file(
                file_path, s3_bucket_name, processing_file_key)

            actual_file_name = file_path.replace('/tmp/', '')
            file_date_timestamp = datetime.strptime(re.search(
                event['re_fileformat'], actual_file_name).group(2), event["re_datepattern"]).strftime('%Y-%m-%d')

            # Get the number of rows in the uploaded CSV file
            number_of_rows = get_row_count_of_s3_by_key(
                s3_bucket_name, processing_file_key)

            file_stat = os.stat(file_path)
            file_metadata = {
                "filename": actual_file_name,
                "processeddate": file_date_timestamp,
                "numberofrows": number_of_rows,
                "filesize": file_stat.st_size,
                "filecategory": event['category']
            }

            insert_processed_file.append(file_metadata)
        except Exception as e:
            print(f"Exception Occured in fn upload_to_s3{e}")
            raise e

    return insert_processed_file


def get_row_count_of_s3_by_key(bucket_name, path):
    # Execute an SQL query to get the row count of a CSV file stored in S3
    s3_client = boto3.client('s3')
    try :
            response = s3_client.get_object(Bucket=bucket_name, Key=path)
            body = response['Body']
            byte_content = body.read()
            # Each row is terminated by a newline character ('\n')
            row_count = byte_content.count(b'\n')
    except Exception as e :
        print(f"Unable to retrive the row count for file from s3 path {path}, error {e}")
        row_count = 0
    return row_count
