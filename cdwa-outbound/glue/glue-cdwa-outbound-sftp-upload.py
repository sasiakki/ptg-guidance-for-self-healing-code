import boto3
import json
from datetime import datetime
import paramiko
import re
from awsglue.utils import getResolvedOptions
import sys


args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account["environment_type"]

if environment_type == "prod":
    # TODO Do not delete this comment: As we are not live in prod, we are still publishing the files to only CDWA SFTP Test folder location. After we receive signoff, change it to Prod folder location.
    sftp_root_dir = "Benefits_Group/Test/To_CDWA/"
    # sftp_root_dir = 'Benefits_Group/Prod/To_CDWA/'
else:
    sftp_root_dir = "Benefits_Group/Test/To_CDWA/"

# Retrieve secrets from AWS Secrets Manager.
secrets_manager_client = boto3.client("secretsmanager")
s3client = boto3.client("s3")
s3resource = boto3.resource("s3")
lambda_client = boto3.client("lambda")

try:
    # Accessing the secrets value for CDWA sftp
    sftp_response = secrets_manager_client.get_secret_value(
        SecretId="{}/b2bds/sftp/cdwa".format(environment_type)
    )

    # Accessing the secrets value for S3 Bucket
    s3response = secrets_manager_client.get_secret_value(
        SecretId="{}/b2bds/s3".format(environment_type)
    )

except Exception as e:
    print(f"Failed to retrieve Secrets Manager secret: {e}")

# Load secret string response into JSON.
try:
    sftp_secrets = json.loads(sftp_response["SecretString"])
    s3_secrets = json.loads(s3response["SecretString"])

except Exception as e:
    print(f"Failed to parse Secrets Manager secret: {e}")

# Get SFTP details from secrets.
try:
    sftp_host = sftp_secrets["host"]
    sftp_port = sftp_secrets["port"]
    sftp_user = sftp_secrets["username"]
    sftp_password = sftp_secrets["password"]

    s3_bucket = s3_secrets["datafeeds"]

except Exception as e:
    print(
        f"Failed to get sftp_secrets, s3_secrets information from Secrets Manager secret: {e}"
    )
    raise Exception(
        "Failed to get sftp_secrets, s3_secrets information from Secrets Manager secret in {}".format(
            environment_type
        )
    )

s3bucket = s3resource.Bucket(s3_bucket)


def write_to_sftpoutboundfilelog(outbound_files_meta_data):
    payload_Glue = {"insert_processed_file": outbound_files_meta_data}
    # Invoke the Lambda function
    lambda_client.invoke(
        FunctionName=environment_type + "-lambda-sftp-db-log-write-cdwa",
        InvocationType="Event",
        Payload=json.dumps(payload_Glue),
    )


def read_from_sftpoutboundfilelog(filecategory):
    payload_Glue = {"category": filecategory}
    # Invoke the Lambda function
    response_for_filecategory = lambda_client.invoke(
        FunctionName=environment_type + "-lambda-sftp-db-log-read-cdwa",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload_Glue),
    )

    latestprocesseddate = json.loads(
        response_for_filecategory["Payload"].read().decode("utf-8")
    )["latestprocesseddate"]

    return latestprocesseddate


def get_row_count_of_s3_csv(bucket_name, path):
    sql_stmt = """SELECT count(*) FROM s3object """
    req = s3client.select_object_content(
        Bucket=bucket_name,
        Key=path,
        ExpressionType="SQL",
        Expression=sql_stmt,
        InputSerialization={
            "CSV": {"FileHeaderInfo": "Use", "AllowQuotedRecordDelimiter": True}
        },
        OutputSerialization={"CSV": {}},
    )
    row_count = 0  # Default value if "Records" key is not found
    for x in req["Payload"]:
        try:
            row_count += int(x["Records"]["Payload"])
        except KeyError:
            # Handle the case when "Records" key is missing
            pass
    return row_count


outboundtypes = [
    {
        "pathfilter": "Outbound/cdwa/Trainee_status_file/",
        "filenameformatprefix": "CDWA-I-BG-TrainingStatusUpdate-",
        "filetypeformatsufix": ".csv",
        "filecategory": "cdwa-trainingstatus",
        "latestprocesseddate": read_from_sftpoutboundfilelog("cdwa-trainingstatus"),
    },
    {
        "pathfilter": "Outbound/cdwa/trainingtransfers_errorlog/",
        "filenameformatprefix": "CDWA-O-BG-TrainingTrans-",
        "filetypeformatsufix": "-error.csv",
        "filecategory": "cdwa-trainingtransfererrors",
        "latestprocesseddate": read_from_sftpoutboundfilelog(
            "cdwa-trainingtransfererrors"
        ),
    },
    {
        "pathfilter": "Outbound/cdwa/providerinfo_errorlog/",
        "filenameformatprefix": "CDWA-O-BG-ProviderInfo-",
        "filetypeformatsufix": "-error.csv",
        "filecategory": "cdwa-providerinfoerrors",
        "latestprocesseddate": read_from_sftpoutboundfilelog("cdwa-providerinfoerrors"),
    },
]

outbound_files_meta_data = []

for outboundtype in outboundtypes:
    for object_summary in s3bucket.objects.filter(Prefix=outboundtype["pathfilter"]):
        if object_summary.key.startswith(
            outboundtype["pathfilter"] + outboundtype["filenameformatprefix"]
        ) and object_summary.key.endswith(outboundtype["filetypeformatsufix"]):
            processingfilekey = object_summary.key
            print(f"S3 File key : {processingfilekey}")
            filename = processingfilekey.replace(outboundtype["pathfilter"], "")
            filedate = re.search(
                r"("
                + outboundtype["filenameformatprefix"]
                + r")(\d\d\d\d-\d\d-\d\d)("
                + outboundtype["filetypeformatsufix"]
                + r")",
                filename,
            ).group(2)
            latestprocesseddate = datetime.strptime(
                outboundtype["latestprocesseddate"], "%Y-%m-%d %H:%M:%S"
            ).date()
            if datetime.strptime(filedate, "%Y-%m-%d").date() > latestprocesseddate:
                rowcount = get_row_count_of_s3_csv(s3_bucket, processingfilekey)
                filecategory = outboundtype["filecategory"]
                filesize = s3client.head_object(
                    Bucket=s3_bucket, Key=processingfilekey
                )["ContentLength"]
                filemetadata = {
                    "processingfilekey": processingfilekey,
                    "filename": filename,
                    "processeddate": filedate,
                    "numberofrows": rowcount,
                    "filesize": filesize,
                    "filecategory": filecategory,
                }
                outbound_files_meta_data.append(filemetadata)

if outbound_files_meta_data:
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(sftp_host, sftp_port, sftp_user, sftp_password)
        sftp = ssh_client.open_sftp()
    except Exception as e:
        print(
            f"Failed to connect to sftp with information from Secrets Manager secret: {e}"
        )
        raise Exception("Failed to connect to CDWA sftp {} site".format(sftp_host))

    print(sftp.listdir(path="Benefits_Group/"))
    for outbound_file_meta_data in outbound_files_meta_data:
        try:
            print('printing outbound_file_meta_data["filename"]')
            print(type(outbound_file_meta_data["filename"]))
            print(outbound_file_meta_data["filename"])
            with sftp.open(
                sftp_root_dir + outbound_file_meta_data["filename"], "w"
            ) as f:
                print(f"starting upload {outbound_file_meta_data['filename']} to sftp")
                s3client.download_fileobj(
                    s3_bucket, outbound_file_meta_data["processingfilekey"], f
                )
                print("done")
        except Exception as e:
            print(
                "Failed to upload {0} file to sftp {1} site".format(
                    outbound_file_meta_data["filename"], sftp_host
                )
            )
            print(f"Failed with reason : {e}")
            raise Exception(
                "Failed to upload {0} file to sftp {1} site".format(
                    outbound_file_meta_data["filename"], sftp_host
                )
            )

    sftp.close()

    write_to_sftpoutboundfilelog(outbound_files_meta_data)
