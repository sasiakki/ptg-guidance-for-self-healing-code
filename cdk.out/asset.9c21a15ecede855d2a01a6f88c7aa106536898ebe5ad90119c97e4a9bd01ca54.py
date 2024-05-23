import boto3
import json
from datetime import datetime
import paramiko
import re
from awsglue.utils import getResolvedOptions
import sys


args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'prod':
    #TODO Don Not delete this comment:  As we not go live in prod we are still publishing the files to only DOH SFTP Test folder location, After we receive signoff the change it to Prod folder location 
    sftp_root_dir = 'BGTest/'
    #sftp_root_dir = 'BGTest/'
else:
    sftp_root_dir = 'BGTest/'



# Retrieve secrets from AWS Secrets Manager.
secrets_manager_client = boto3.client('secretsmanager')
s3client = boto3.client('s3')
s3resource = boto3.resource('s3')
lambda_client = boto3.client('lambda')

try:
    #Accessing the secrets value for DOH sftp
    sftp_response = secrets_manager_client.get_secret_value(
    SecretId="{}/b2bds/sftp/doh".format(environment_type))
    
    #Accessing the secrets value for S3 Bucket
    s3response = secrets_manager_client.get_secret_value(
        SecretId="{}/b2bds/s3".format(environment_type))
    
except Exception as e:
    print(f"Failed to retrieve Secrets Manager secret: {e}")
    
# Load secret string response into JSON.
try:
    sftp_secrets = json.loads(sftp_response['SecretString'])
    
    s3_secrets = json.loads(s3response['SecretString'])
    
except Exception as e:
    print(f"Failed to parse Secrets Manager secret: {e}")
# Get SFTP detaiils from secrets.
try:
    sftp_host = sftp_secrets['host']
    sftp_port = sftp_secrets['port']
    sftp_user = sftp_secrets['username']
    sftp_password = sftp_secrets['password']
    
    s3_bucket = s3_secrets['datafeeds']
    
except Exception as e:
    print(f"Failed to get sftp_secrets ,s3_secrets information from Secrets Manager secret: {e}")
    raise Exception ("Failed to get sftp_secrets ,s3_secrets information from Secrets Manager secret in {}".format(environment_type))



## Processing Trainee_status_file to DOH SFTP Client


s3bucket = s3resource.Bucket(s3_bucket)


def write_to_sftpoutboundfilelog(outbound_files_meta_data):
   
    payload_Glue = { "insert_processed_file": outbound_files_meta_data }
    # Invoke the Lambda function
    lambda_client.invoke(
        Functionname=environment_type+'-lambda-sftp-db-log-write-doh',
        InvocationType='Event',  
        Payload=json.dumps(payload_Glue) 
    )
    
def read_from_sftpoutboundfilelog(filecategory):
    
    payload_Glue = { "category": filecategory }
    # Invoke the Lambda function
    response_for_filecategory = lambda_client.invoke(
        Functionname=environment_type+'-lambda-sftp-db-log-read-doh',
        InvocationType='RequestResponse',  
        Payload=json.dumps(payload_Glue) 
    )
    
    latestprocesseddate = json.loads(response_for_filecategory['Payload'].read().decode("utf-8"))['latestprocesseddate']
    
    return latestprocesseddate


def get_row_count_of_s3_file_by_key(bucket_name, path) :
    response = s3client.get_object(Bucket=bucket_name, Key=path)
    content = response['Body'].read().decode('utf-8')
    row_count = len(content.split('\n'))
    return row_count

outboundtypes = [
    {
        "pathfilter":"Outbound/doh/classified/",
        "filenameformatprefix":"Classified_DOH_BT75_Students_",
        "filetypeformatsufix":"_1.txt",
        "filecategory": "doh-classified",
        "latestprocesseddate":read_from_sftpoutboundfilelog("doh-classified")
     }

     
]
outbound_files_meta_data = []



for outboundtype in outboundtypes:
    for object_summary in s3bucket.objects.filter(Prefix=outboundtype["pathfilter"]):
        if object_summary.key.startswith(outboundtype["pathfilter"]+outboundtype["filenameformatprefix"]) and object_summary.key.endswith(outboundtype["filetypeformatsufix"]):
            processingfilekey = object_summary.key
            filename = processingfilekey.replace(outboundtype["pathfilter"],"")
            print(filename)
            filedate = re.search(r"("+outboundtype["filenameformatprefix"]+")(\d\d_\d\d_\d\d\d\d)("+outboundtype["filetypeformatsufix"]+")", filename).group(2)
            #rowcount = get_row_count_of_s3_csv(s3_bucket, processingfilekey)
            rowcount = get_row_count_of_s3_file_by_key(s3_bucket, processingfilekey)
            filecategory = outboundtype["filecategory"]
            filesize = s3client.head_object(Bucket=s3_bucket, Key=processingfilekey)['ContentLength']
            tmp_filedate = datetime.strptime(filedate, '%m_%d_%Y').date()
            filemetadata = {"processingfilekey":processingfilekey,"filename":filename,"processeddate":filedate,"numberofrows":rowcount,"filesize":filesize,"filecategory":filecategory}
            latestprocesseddate = datetime.strptime(outboundtype["latestprocesseddate"], '%Y-%m-%d %H:%M:%S').date()
            if tmp_filedate > latestprocesseddate:
                outbound_files_meta_data.append(filemetadata)

if outbound_files_meta_data:
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        ssh_client.connect(sftp_host,sftp_port,sftp_user,sftp_password)
        sftp = ssh_client.open_sftp()
    except Exception as e:
       print(f"Failed to connect to sftp with information from Secrets Manager secret: {e}")
       raise Exception ("Failed to connect to DOH sftp {} site".format(sftp_host))
        
    print(sftp.listdir(path='BGTest/'))
    for outbound_file_meta_data in outbound_files_meta_data:
        try:
            print('printing outbound_file_meta_data["filename"]')
            print(type(outbound_file_meta_data["filename"]))
            print(outbound_file_meta_data["filename"])
            with sftp.open(sftp_root_dir+outbound_file_meta_data["filename"], 'w') as f:
                print(f"starting upload {outbound_file_meta_data['filename']} to sftp")
                s3client.download_fileobj(s3_bucket, outbound_file_meta_data["processingfilekey"], f)
                print("done")
        except Exception as e:
            print("Failed to upload {0} file to sftp {1} site".format(outbound_file_meta_data["filename"] ,sftp_host))
            print(f"Failed with reason : {e}")
            raise Exception ("Failed to upload {0} file to sftp {1} site".format(outbound_file_meta_data["filename"] ,sftp_host))
    
    sftp.close()
    
    write_to_sftpoutboundfilelog(outbound_files_meta_data)
