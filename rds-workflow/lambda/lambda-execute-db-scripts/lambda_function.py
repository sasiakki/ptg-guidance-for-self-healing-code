import psycopg2
import os
import boto3
import json
import glob
import boto3, json, os, glob

def lambda_handler(event, context):

    #ENTER YOUR TICKET NUMBER HERE AS A COMMENT FOR EVERY RDS DB SCRIPTS CHANGE
    #B2BDS-2134

    # Get a list of all files in the folder
    folder_path = '/tmp'
    file_list = os.listdir(folder_path)

    environment_type = os.environ['environment_type']

    #get sts client
    sts_client = boto3.client("sts")

    # Get the bucket name based on the env type
    secrets_manager_client = boto3.client('secretsmanager')
    try:
        s3_response = secrets_manager_client.get_secret_value(
            SecretId="{}/b2bds/s3".format(environment_type))
    except Exception as e:
        print(f"Failed to retrieve Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to retrieve Secrets Manager secret.','result': False}
    # Load secret string response into JSON.
    try:
        s3_secrets = json.loads(s3_response['SecretString'])
    except Exception as e:
        print(f"Failed to parse Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to parse Secrets Manager secret.','result': False}
    # Get S3 bucket from secrets.
    try:
        s3_bucket_name = s3_secrets['dbscripts']
    
    except Exception as e:
        print(f"Failed to get S3 bucket information from Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to get S3 bucket information from Secrets Manager secret.','result': False}


    #Download the db scripts from the S3 bucket
    # Create an S3 client
    s3_client = boto3.client('s3')    

    print("Download the files from S3 bucket to /tmp folder")
    s3resource = boto3.resource('s3')
    s3bucket = s3resource.Bucket(s3_bucket_name)

    for object_summary in s3bucket.objects.filter(Prefix='db_scripts'):
        print(f"Processing S3 bucket File: {object_summary.key}")
        if object_summary.key.endswith('sql'):
            print('Copying the file : ' + object_summary.key)
            file_name = os.path.basename(object_summary.key)
            local_file_path = os.path.join('/tmp', file_name)
            s3_client.download_file(s3_bucket_name, object_summary.key, local_file_path)


    # # List objects in the specified folder
    # response = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix='db_scripts')
    # # Download the objects from the specified folder
    # for obj in response.get('Contents', []):
    #     s3_key = obj['Key']
    #     file_name = os.path.basename(s3_key)
    #     if file_name.endswith(".sql"):
    #         print('Copying the file : ' + file_name)
    #         local_file_path = os.path.join('/tmp', file_name)
    #         s3_client.download_file(s3_bucket_name, s3_key, local_file_path)

    # Accessing the secrets target database
    databaseresponse = secrets_manager_client.get_secret_value(
        SecretId=environment_type+'/b2bds/rds/cicd-pipelines'
    )
    database_secrets = json.loads(databaseresponse['SecretString'])
    B2B_USER = database_secrets['username']
    B2B_PASSWORD = database_secrets['password']
    B2B_HOST = database_secrets['host']
    B2B_PORT = database_secrets['port']
    B2B_DBNAME = database_secrets['dbname']
    
    conn = psycopg2.connect(host=B2B_HOST, port=B2B_PORT,
                database=B2B_DBNAME, user=B2B_USER,
                password=B2B_PASSWORD)

    cursor = conn.cursor()

    root_dir = os.getcwd()
    # Iterate over the files in the root directory
    all_sql_scripts=[]
    print('Parse the /tmp folder and execute the sql files')
    try:
        #get files from code commit
        roleArn="arn:aws:iam::938426161301:role/workflow-cleanup-role"
        roleSessionName="938426161301-codecommit-cleanup-role"
        response = sts_client.assume_role(RoleArn=roleArn, RoleSessionName=roleSessionName,DurationSeconds=900)
        another_account_client = boto3.Session(
            aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
            aws_session_token=response["Credentials"]["SessionToken"]
            )
        codecommit_client = another_account_client.client('codecommit', region_name='us-west-2')
        response = codecommit_client.get_folder(
            repositoryName='datastore-cdk-repo',
            folderPath='db_scripts'
        )
        code_commit_files = response['files']

        sql_files = glob.glob('/tmp/*')
        print("Sql scripts being executed:")
        print(sql_files)
        #execute each sql file
        for file in sql_files:
            for codecommitFile in code_commit_files:
                #process files which are present in s3 and code-commit
                if(codecommitFile['relativePath']==file[5:]):
                    with open(file, "r",encoding='utf-8') as f:
                        print('deploying the file: ' + file)
                        # Read the file contents
                        content = f.read()
                        wrapped_contents = content
                        cursor.execute(wrapped_contents)
                    break
                else:
                    continue
        conn.commit()
    except Exception as e:
        print(e)
        print('Cleaning the /tmp folder')
        # Iterate over the files and delete the ones ending with ".sql"
        for file_name in file_list:
            if file_name.endswith(".sql"):
                print('deleting file ' + file_name)
                file_path = os.path.join(folder_path, file_name)
                os.remove(file_path)
        raise Exception ("Failed to execute the sql scripts ")
    finally:
        conn.close()

    print('All scripts executed successfully')
    # Delete the files  from the s3 bucket
    response = s3_client.list_objects_v2(Bucket=s3_bucket_name, Prefix='db_scripts')

    # Extract the object keys from the response
    object_keys = [obj['Key'] for obj in response.get('Contents', [])]

    #Delete files from /tmp
    # Get a list of all files in the folder
    folder_path = '/tmp'
    file_list = os.listdir(folder_path)

    print('Cleaning the /tmp folder')
    # Iterate over the files and delete the ones ending with ".sql"
    for file_name in file_list:
        if file_name.endswith(".sql"):
            print('deleting file ' + file_name)
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)

    print('Cleaning up the S3 bucket')
    # Delete the objects from the specified folder
    if len(object_keys) > 0:
        print('Deleting the following files from s3 bucket')
        for key in object_keys:
            print(key)
        response = s3_client.delete_objects(
            Bucket=s3_bucket_name,
            Delete={'Objects': [{'Key': key} for key in object_keys]}
        )
        if 'Errors' in response:
            print('Error occurred during deletion:')
            for error in response['Errors']:
                print(f"- {error['Key']}: {error['Message']}")
    else:
        print("No objects found in folder: db_scripts")
        
    if environment_type == 'prod':
        roleArn="arn:aws:iam::938426161301:role/workflow-cleanup-role"
        roleSessionName="938426161301-codecommit-cleanup-role"
        response = sts_client.assume_role(RoleArn=roleArn, RoleSessionName=roleSessionName,DurationSeconds=900)
        another_account_client = boto3.Session(
            aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
            aws_session_token=response["Credentials"]["SessionToken"]
            )
        codecommit_client = another_account_client.client('codecommit', region_name='us-west-2')    
        print('Cleaning up the Codecommit Repo')
        response = codecommit_client.get_folder(
            repositoryName='datastore-cdk-repo',
            folderPath='db_scripts'
        )

        for file in response['files']:
            dev_branch = codecommit_client.get_branch(
                    repositoryName='datastore-cdk-repo',
                    branchName='development'
                )
            latest_commit_id = dev_branch['branch']['commitId']
            file_name = file['relativePath']
            if file_name.endswith('.sql'):
                print('Deleting file '+file['relativePath']+ ' from Codecommit')
                codecommit_client.delete_file(
                        repositoryName='datastore-cdk-repo',
                        branchName='development',
                        filePath=file['absolutePath'],
                        parentCommitId=latest_commit_id,
                        keepEmptyFolders=True,
                        commitMessage=f'Codecommit cleanup of file: {file_name}'
                )
                print('Deleted file from CodeCommit: ' + file['absolutePath'])
    else:
        pass    

    return {'message': 'SQL scripts executed successfully'}


if __name__ == "__main__":
  lambda_handler()