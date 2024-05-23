
import json
import os
import boto3
import psycopg2
from psycopg2 import sql			   
from datetime import datetime
import re
import pandas as pd

client10 = boto3.client('secretsmanager')

response1 = client10.get_secret_value(
    SecretId='prod/b2bds/rds/system-pipelines'
)

execute_string = """"""

database_secrets = json.loads(response1['SecretString'])

B2B_USER = database_secrets['username']
B2B_PASS = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_NAME = 'b2bds'
#Function to clean the event structure and gather the columns hence create a dataframe
def event_df(event):
  name_dict= ("FirstName","LastName","MiddleName")
  wanted= ('personid','firstname','lastname','middlename','ssn','dob','email1',
		'email2','homephone','mobilephone','language','mailingstreet1','mailingstreet2',
		'mailingcity','mailingstate','mailingzip','mailingcountry','Learner_Status__c',
		'exempt','status','hiredate','LastModifiedDate','Worker_Category__c','sfcontactid','mailingaddress','physicaladdress',
		'workercategory','iscarinaeligible','ahcas_eligible','matched_sourcekeys','type','recordmodifieddate')
  dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
  Person_json = event
 # filtereddict = dictfilt(Person_json['detail'], wanted)
  if Person_json['detail'].get('Name') == None:
    name_dictfilt = {}
  else:
      name_dictfilt = dictfilt(Person_json['detail']['Name'], name_dict) 
  name_dictfilt.update(Person_json['detail'])
  if Person_json['detail'].get('PhysicalAddress') == None:
    physical_address = ''  
  else:
    physical_dict = {'Street': '', 'City': '', 'State': '','PostalCode':'','Country':''}
    physical_add = {k:(Person_json['detail']['PhysicalAddress'][k] if k in Person_json['detail']['PhysicalAddress'] else v) for k,v in physical_dict.items()}
    physical_address = ' '.join(map(str, physical_add.values()))
  maildict=('MailingStreet1','MailingStreet2','City','State','PostalCode','Country')
  if Person_json['detail'].get('MailingAddress') == None:
    mailing_address = ''
    mail_dict={}
  else:
    mailing_dict = {'MailingStreet1': '','MailingStreet2':'', 'City': '', 'State': '','PostalCode':'','Country':''}
    if 'detail' in Person_json and 'MailingAddress' in Person_json['detail'] and 'Street' in Person_json['detail']['MailingAddress']:
      street = Person_json['detail']['MailingAddress']['Street'].split("\n")
      Person_json['detail']['MailingAddress']['MailingStreet1'] = street[0]
      Person_json['detail']['MailingAddress']['MailingStreet2'] = street[1] if len(street) > 1 else None
      Person_json['detail']['MailingAddress'].pop("Street")
    mailing_dict = {k:(Person_json['detail']['MailingAddress'][k] if k in Person_json['detail']['MailingAddress'] else v) for k,v in mailing_dict.items()}
    mail_dict = dictfilt(Person_json['detail']['MailingAddress'], maildict) 
    mailing_address = ' '.join(map(str, mailing_dict.values()))
  name_dictfilt.update(mail_dict)

  dic = {'sfcontactid':'','mailing_address':'','physical_address':''}
  for key, value in dic.items():
    dic['sfcontactid'] = Person_json['detail']['ChangeEventHeader']['recordIds'][0]
    dic['mailing_address'] = mailing_address
    dic['physical_address'] = physical_address
  name_dictfilt.update(dic)
  keymap = {
    "Person_Id_Sync__c": "personid",
    "FirstName": "firstname",
    "LastName": "lastname",
    "MiddleName": "middlename",
    "Social_Security_Last_4__c": "ssn",
    "Birthdate": "dob",
    "Email": "email1",
    "Email_2__c": "email2",
    "Phone": "homephone",
    "OtherPhone": "mobilephone",
    "Language_Assignment__c": "language",
    "MailingStreet1": "mailingstreet1",
    "MailingStreet2":"mailingstreet2",						  
    "City": "mailingcity",
    "State": "mailingstate",
    "PostalCode": "mailingzip",
    "Country":"mailingcountry",
    "My_Preferred_Language_is__c":"language",
    "Learner_Status__c": "trainingstatus",
    "Exempt_by_Employment__c": "exempt",								
    "Employment_Status__c": "status",
    "Hire_Date__c": "hiredate",
    "sfcontactid":"sfcontactid",
    "mailing_address":"mailingaddress",
    "physical_address":"physicaladdress",
    "Worker_Category__c": "workercategory",
    "Carina_Eligible__c": "iscarinaeligible",
    "AHCAS_Elegible__c": "ahcas_eligible",
    "sourcekey": "matched_sourcekeys",
    "Provider_Type__c": "type"}
  filtereddict = {keymap.get(k, k): v for k, v in name_dictfilt.items()}
  #filtereddict.update(dic)
  #Check if the value is a string after iterating over the key-value pairs, if so apply the
  #strip() method to remove any leading or trailing whitespace
  filtereddict = {k: v.strip() if isinstance(v, str) else v for k, v in filtereddict.items()}
  Final_df = dictfilt(filtereddict, wanted)
  personid_split = Final_df['personid'].split("_", 1)
  pid = personid_split[0]
  for key, value in Final_df.items():
    Final_df['personid'] = pid
  Final_df = {key:value for (key, value) in Final_df.items() if value !=''}
  Final_df['recordmodifieddate']= datetime.now().isoformat()

  return Final_df
   
   
   
def lambda_handler(event, context):
    print(event)
    username = B2B_USER
    password = B2B_PASS
    host_name = B2B_HOST
    port = B2B_PORT
    db_name = B2B_NAME
    dataFrame = event_df(event)
    print(dataFrame)
    dbO = b2b_conn()
    dbO.insert_(dataFrame);
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
   
#Connecting to the database     
class b2b_conn():
    def __init__(self):
        self.conn = self.sqldb_connection()

    def sqldb_connection(self):
        username = B2B_USER
        password = B2B_PASS
        host_name = B2B_HOST
        port = B2B_PORT
        db_name = B2B_NAME
        
        conn = psycopg2.connect(database=db_name, user=username, password=password, 
                                  host=host_name,port=port)
        conn.autocommit = True
        return conn

#function to update data into the database        
    def insert_(self, df):
        person_id = df['personid']
        maildict=('mailingstreet1','mailingstreet2','mailingcity','mailingstate','mailingzip','mailingcountry')
        missing_fields = [field for field in maildict if field not in df]
        if len(missing_fields) != len(maildict):
          select_query = "SELECT " + ", ".join(missing_fields) + " FROM prod.person where personid = %(person_id)s"
          json_address= pd.read_sql_query(select_query ,self.conn, params={"person_id":person_id})
          result_dict = json_address.iloc[0].to_dict()
          result_dict.update(df)
          print(result_dict)
          mailing_dict = {'mailingstreet1': '','mailingstreet2':'', 'mailingcity': '', 'mailingstate': '','mailingzip':'','mailingcountry':''}
          mailing_dict = {k:(result_dict[k] if k in result_dict else v) for k,v in mailing_dict.items()}
          partial_address = ' '.join([value for value in mailing_dict.values()])
          df['mailingaddress'] = partial_address
          print(df)
          update_fields = list(df.keys())
        else:
          update_fields = list(df.keys())
        update_sql = sql.SQL("""UPDATE prod.person SET ({}) = ({}) WHERE personid = %(personid)s """).format(sql.SQL(", ").join(map(sql.Identifier, update_fields)),sql.SQL(", ").join(map(sql.Placeholder, update_fields)))
        cur = self.conn.cursor()
    
        try:
            cur.execute(update_sql,df)

            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            self.conn.rollback()			   
            cur.close()
            self.conn.close()
            return 1
        print("execute sql() done")
        cur.close()
        self.conn.close()
        
		
		
            
        
        
        
 

