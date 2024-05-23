import json
import boto3
import os

def lambda_handler_all(event, context):
    
    checkpaths = ['studentRegistrationReport','01250_TPExam_ADSAToTP','CDWA-O-BG-TrainingTrans','CDWA-O-BG-ProviderInfo','01250_TPCertification_ADSAToTP','HMCC - DSHS Benefit',
    'DSHS_O&S_Completed','01250_TPExam_ADSAToTP','PCSS_TP_New_Provider_Enrollment','Caregiverdata','O&SCompletion','01250_RelDOBLang_ADSAToTP','SmartSheet','Qualtricstrainingtransfers','Docebocoursecompletions',
    'Transfer hours']
    
    environment_type = os.environ['environment_type']
    
    # Accessing the Secrets Manager from boto3 lib s
    secretsmangerclient = boto3.client('secretsmanager') 
    # Accessing the secrets value for S3 Bucket 
    s3response = secretsmangerclient.get_secret_value( SecretId=environment_type+'/b2bds/s3' ) 
    s3_secrets = json.loads(s3response['SecretString']) 
    S3_BUCKET = s3_secrets['datafeeds']


    s3_resource = boto3.resource('s3')    
    s3bucket = s3_resource.Bucket(S3_BUCKET)
    
    # Listiing out all objects in respective paths

    objects_exam = list(s3bucket.objects.filter(Prefix='Inbound/raw/exam/'))
    
    objects_cdwa_providerinfo = list(s3bucket.objects.filter(Prefix='Inbound/raw/cdwa/ProviderInfo/'))
    
    objects_credential = list(s3bucket.objects.filter(Prefix='Inbound/raw/credential/'))
    
    objects_doh_classified = list(s3bucket.objects.filter(Prefix='Inbound/raw/doh/classified/'))
    
    objects_doh_completed = list(s3bucket.objects.filter(Prefix='Inbound/raw/doh/completed/'))

      
    objects_dshs_qual_os = []
    for object_dshs_qual_os in s3bucket.objects.filter(Prefix='Inbound/raw/qualtrics/DSHS_O&S_Completed/'):
          if object_dshs_qual_os.key.endswith('csv'):
            objects_dshs_qual_os.append(object_dshs_qual_os.key)
    

    objects_caregiver_intake = list(s3bucket.objects.filter(Prefix='Inbound/raw/qualtrics/caregiver_intake/'))

    
    objects_qual_os = []
    for object_qual_os in s3bucket.objects.filter(Prefix='Inbound/raw/qualtrics/O&SCompletion/'):
          if object_qual_os.key.endswith('csv'):
            objects_qual_os.append(object_qual_os.key)
    
    objects_reldob = list(s3bucket.objects.filter(Prefix='Inbound/raw/reldob/'))
    
    objects_smartsheets = list(s3bucket.objects.filter(Prefix='Inbound/raw/smartsheets/curated/'))

    objects_cdwa_trainingtransfer = list(s3bucket.objects.filter(Prefix='Inbound/raw/cdwa/trainingtransfer'))
    
    objects_cornerstone = list(s3bucket.objects.filter(Prefix='Inbound/raw/cornerstone/'))
    
   
    #This for Manual transfersfile provided by BA's monthly
    objects_manualtransferhours = list(s3bucket.objects.filter(Prefix='Inbound/raw/manualtransferhours/'))
    
    objects_docebo = list(s3bucket.objects.filter(Prefix='Inbound/raw/docebo/')) 

    objects_all = objects_exam + objects_cdwa_providerinfo + objects_credential + objects_doh_classified + objects_doh_completed + objects_caregiver_intake +  objects_reldob + objects_smartsheets + objects_cdwa_trainingtransfer + objects_manualtransferhours + objects_dshs_qual_os + objects_caregiver_intake + objects_docebo + objects_cornerstone
    
    print(objects_all)
    
    for each_object in objects_all: 
        for filename in checkpaths:
            if filename in str(each_object):
                print(filename)
                return {'statusCode': 200,
                'objects': True
            } 
    return {'statusCode': 200,
            'objects': False
        }