import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col,current_date,coalesce,concat,rank,concat_ws,when,collect_set,lit,to_date,date_format,current_timestamp
from awsglue.transforms import *
from awsglue.dynamicframe import DynamicFrame
from datetime import datetime,date
import pandas
import boto3
import json


## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Setting the timeParserPolicy as legacy for handling multiple types of date formats received in qualtrics responses 
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

#Capturing the current date to append to filename
today = datetime.now()
suffix = today.strftime("%Y%m%d%H%M%S")

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'
    
#Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

#Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3'
)
s3_secrets = json.loads(s3response['SecretString'])
S3_BUCKET = s3_secrets['datafeeds']

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/rds/system-pipelines'
)
database_secrets = json.loads(databaseresponse['SecretString'])
B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_DBNAME = database_secrets['dbname']

url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

#Capturing the Delta Agency person os completions data from raw tables
agency_person = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_os_qual_agency_person").toDF()

#Capturing lastprocessed datetime from logs.lastprocessed
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_logs_lastprocessed").toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")

# Capturing only new responses based on delta detection process
agency_person = agency_person.filter("isdelta == 'true'")

# Formatting for multiple types of date formats received in response 
agency_person = agency_person.withColumn("os_completion_date", coalesce(*[to_date("os_completion_date", f) for f in ("MM/dd/yyyy","MM-dd-yyyy", "yyyy-MM-dd","MMddyyyy")]))

#Registering the temp view for formatted data
agency_person.createOrReplaceTempView("os_qual_agency_person")

#Registering the temp view for prod person table 
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name= catalog_table_prefix+"_prod_person"
).toDF().selectExpr("*").createOrReplaceTempView("person")


if (agency_person.count() > 0):
    #Registering the temp view for formatted data
    agency_person.createOrReplaceTempView("os_qual_agency_person")
    # Handling the duplicate in same file received as additional response
    infileduplicatesdf = spark.sql(""" 
                                   with oscompletions as (select person_id,os_completion_date, filemodifieddate as filedate,filename,finished, ROW_NUMBER () OVER ( PARTITION BY person_id ORDER BY filemodifieddate DESC, os_completion_date ASC ) completionsrank from os_qual_agency_person
                                   WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-qualtrics-os-completions-raw-to-raw-traininghistory' AND success='1') )
                                   select cast(person_id as long) as personid 
                                    ,os_completion_date as completeddate
                                    ,filename
                                    ,filedate
                                    ,'Orientation & Safety EN' as coursename
                                    ,5 as credithours 
                                    ,'1000065ONLEN02' as courseid
                                    ,100 as trainingprogramcode
                                    ,'Orientation & Safety' as trainingprogramtype
                                    ,'EN' as courselanguage
                                    ,'ONL' as coursetype
                                    ,'YOUTUBE' as trainingsource
                                    ,'NA' as instructorname
                                    ,'NA' as instructorid 
                                    ,'Duplicate in same file received as additional response' as error_message
                                    from oscompletions where completionsrank > 1
                                   """) 


    #Prod Person table for validating the personid are same 
    spark.sql("""with oscompletions as (select person_id,os_completion_date, filemodifieddate, finished,filename,ROW_NUMBER () OVER ( PARTITION BY person_id ORDER BY filemodifieddate DESC, os_completion_date ASC ) completionsrank from os_qual_agency_person WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-qualtrics-os-completions-raw-to-raw-traininghistory' AND success='1')) select cast(person_id as long) as personid,os_completion_date, filemodifieddate, finished,filename from oscompletions where completionsrank = 1 """).createOrReplaceTempView("os_qual_agency_person")

    # evaluating the OS completions personids with valid prod person personid's for  valid personid's 
    traininghistory = spark.sql("""with oscompletions as (select personid,os_completion_date, filemodifieddate,filename from os_qual_agency_person where finished = '1' ), person as (select distinct personid from person where personid is not null)
                                select pr.personid ,o.os_completion_date as completeddate,'Orientation & Safety EN' as coursename ,5 as credithours ,'1000065ONLEN02' as courseid ,100 as trainingprogramcode ,'Orientation & Safety' as trainingprogramtype ,'EN' as courselanguage,'ONL' as coursetype,'YOUTUBE' as trainingsource, 'NA' as instructorname, 'NA' as instructorid ,o.filemodifieddate,o.filename from oscompletions o left join person pr on o.personid = pr.personid
                                where pr.personid is not null
                                """)


    traininghistory.show()
    traininghistory.printSchema()

    # Coverting  spark dataframe to glue dynamic dataframe
    newdatasource0 = DynamicFrame.fromDF(traininghistory, glueContext, "newdatasource0")                            
                                

    # ApplyMapping to match the target table
    applymapping1 = ApplyMapping.apply(frame = newdatasource0, mappings = [
        ("personid", "long", "personid", "long"),
        ("dshsid", "long", "dshsid", "long"),
        ("courseid", "string", "courseid", "string"),
        ("completeddate","date","completeddate","date"),
        ("coursename","string","coursename","string"),
        ("credithours","int","credithours","double"),
        ("trainingprogramtype", "string", "trainingprogramtype", "string"),
        ("trainingprogramcode", "int", "trainingprogramcode", "long"),
        ("coursetype", "string", "coursetype", "string"),
        ("courselanguage", "string", "courselanguage", "string"),
        ("instructorname", "string", "instructorname", "string"),
        ("instructorid", "string", "instructorid", "string"),
        ("trainingsource", "string", "trainingsource", "string"),
        ("filemodifieddate", "timestamp", "filedate", "timestamp"),
        ("filename", "string", "filename", "string"),    
        ], transformation_ctx = "applymapping1")
                           
    selectfields2 = SelectFields.apply(frame = applymapping1, paths = ["personid","courseid","completeddate", "coursename","credithours", "trainingprogramtype", "trainingprogramcode", "coursetype", "courselanguage","instructorname","instructorid", "trainingsource","filedate","filename"], transformation_ctx = "selectfields2")

    resolvechoice3 = ResolveChoice.apply(frame = selectfields2, choice = "MATCH_CATALOG", database = catalog_database, table_name = catalog_table_prefix+"_raw_traininghistory", transformation_ctx = "resolvechoice3")

    resolvechoice4 = DropNullFields.apply(frame = resolvechoice3, transformation_ctx = "resolvechoice4")

    datasink5 = glueContext.write_dynamic_frame.from_catalog(frame = resolvechoice4, database = catalog_database, table_name = catalog_table_prefix+"_raw_traininghistory", transformation_ctx = "datasink5")

    #evaluating the OS completions personids with valid prod person personid's for invalid personid's 
    traininghistorylog = spark.sql("""with oscompletions as (select personid,os_completion_date, filemodifieddate as filedate,filename from os_qual_agency_person where finished = '1' ), person as (select distinct personid from person where personid is not null)
                                select 
                                     o.personid 
                                    ,o.os_completion_date as completeddate
                                    ,filename
                                    ,filedate
                                    ,'Orientation & Safety EN' as coursename
                                    ,5 as credithours 
                                    ,'1000065ONLEN02' as courseid
                                    ,100 as trainingprogramcode
                                    ,'Orientation & Safety' as trainingprogramtype
                                    ,'EN' as courselanguage
                                    ,'ONL' as coursetype
                                    ,'YOUTUBE' as trainingsource
                                    ,'NA' as instructorname
                                    ,'NA' as instructorid 
                                    ,'PersonID Mismatch' as error_message
                                    from oscompletions o left join person pr on o.personid = pr.personid
                                where pr.personid is null
                                """)

    traininghistorylog = traininghistorylog.unionByName(infileduplicatesdf)

    traininghistorydf=traininghistorylog.toPandas()
    #Writing qualtrics o&s raw to raw traininghistory logs to csv
    traininghistorydf.to_csv("s3://"+S3_BUCKET+"/Outbound/qualtrics/errorlog/raw_to_raw_traininghistory_error_"+suffix+".csv", header=True, index=None, sep=',')

    errorcdf = DynamicFrame.fromDF(traininghistorylog, glueContext, "errorcdf")

    glueContext.write_dynamic_frame.from_catalog(
        frame=errorcdf,
        database=catalog_database,
        table_name=catalog_table_prefix+"_logs_traininghistorylog",
    )

    print("Insert an entry into the log table")
    max_filedate = datetime.now()
    logs_data = [[ max_filedate, "glue-qualtrics-os-completions-raw-to-raw-traininghistory", "1"]] 		 
    logs_columns = ['lastprocesseddate', 'processname','success'] 		 
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
    mode = 'append'  		 
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
else:
    print("Data has already processed or no new data in the source table.")

print("****************Job execution completed*******************")
job.commit()