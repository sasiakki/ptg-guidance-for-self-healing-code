import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
import pandas
from datetime import datetime
import boto3
import json
import csv

args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account['environment_type']

if environment_type == 'dev':
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets value for S3 Bucket
s3response = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/s3'
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

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')

#Default Job Arguments
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

print("****************Starting Job execution*******************")
#Setting leagacy parser to handle multiple date formats
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")

#Capturing all the docebo completions
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_raw_docebo_course_completion",
    transformation_ctx = "raw_docebo_course_completion").toDF().createOrReplaceTempView("raw_docebo_course_completion")

# Script generated for node PostgreSQL
prodpersondf = glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_prod_person",
    transformation_ctx = "prod_person").toDF()
    
#Removing blank spaces for all columns
prodpersondf = prodpersondf.select([when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c) for c in prodpersondf.columns])

prodpersondf.createOrReplaceTempView("prodperson")
    
# Script generated for node PostgreSQL
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_coursecatalog",
).toDF().createOrReplaceTempView("coursecatalog")

#Capturing lastprocessed datetime from logs.lastprocessed
## B2BDS-1340: Access the lastprocessed log table and create a DF for Delta Detection purpose
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, 
    table_name=catalog_table_prefix+"_logs_lastprocessed"
 ).toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")

#Extracted the data from Database
raw_docebo_completion_df = spark.sql("""   select username as personid
                     , firstname
                     , lastname
                     , dshsid
                     , credithours
                     , to_date(completiondate,'MM/dd/yyyy') as completiondate
                     , trim(lastname) as lastname
                     , trim(firstname) as firstname
                     , coursecode
                     , coursename
                     , dshscode
                     , filename
                     , filedate
        from raw_docebo_course_completion WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-docebo-coursecompletions-raw-to-raw-traininghistory' AND success='1') """)

if (raw_docebo_completion_df.count() > 0):        
    raw_docebo_completion_df.createOrReplaceTempView("raw_docebo_course_completion")
    #raw_docebo_completion_df.show()
    print ("Total records from raw : {0}".format(raw_docebo_completion_df.count()))

    ## Identify and flagging valid and invalid records if personid not found in prod person table
    raw_docebo_course_completion_valid_flag_df = spark.sql("""select ds.*, 
                    CASE WHEN pr.personid is null or completiondate > current_date THEN 0 ELSE 1 END ValidInd,
                    CASE 
                     WHEN pr.personid is null THEN 'PersonID is not Valid'
                     WHEN completiondate > current_date THEN 'Completion Date is in the Future'
                 END ValidIndERR
              from raw_docebo_course_completion ds left join prodperson pr on ds.personid = pr.personid""")
    raw_docebo_course_completion_valid_flag_df.createOrReplaceTempView("raw_docebo_course_completion_valid_flag")
    #raw_docebo_course_completion_valid_flag_df.show()

    ## identifying duplicate records based on personid,coursecode getting earliest record and flagging valid and invalid records
    raw_docebo_course_completion_duplicate_errors_df = spark.sql("select personid,credithours,completiondate,coursecode,coursename,dshscode,filename,filedate,\
                CASE WHEN completionsrank>1 then 'Course Completion is Redundant' end as ValidIndERR, \
                CASE WHEN completionsrank>1 then 0 else 1 end as ValidInd \
                from (select *, row_number() over (Partition by personid,coursecode ORDER BY  completiondate ASC ) completionsrank \
                from  raw_docebo_course_completion_valid_flag where ValidInd=1) DS")
    raw_docebo_course_completion_duplicate_errors_df.createOrReplaceTempView("raw_docebo_course_completion_duplicate_errors")
    #raw_docebo_course_completion_duplicate_errors_df.show()

    ## Filtering invalid courseid and coursename and flagging valid and invalid records
    raw_docebo_course_completion_coursename_errors_df = spark.sql("select personid,cs.credithours,cs.coursename,coursecode,completiondate,dshscode,filename,filedate, \
               CASE WHEN tc.courseid is null or cs.coursecode is null then 'CourseID is not Valid' WHEN cs.coursename is null or tc.coursename is null then 'CourseName is not Valid' WHEN cast(cs.credithours as double)>cast(tc.credithours as double) then 'Credit Hours is not Valid' end as ValidIndERR, \
               CASE WHEN tc.coursename is null or tc.courseid is null or cs.coursecode is null or cs.coursename is null or (cast(cs.credithours as double)>cast(tc.credithours as double)) then 0 else 1 end as ValidInd \
              from raw_docebo_course_completion_duplicate_errors cs left join coursecatalog tc on trim(lower(tc.courseid)) = trim(lower(cs.coursecode)) where cs.ValidInd=1")
    raw_docebo_course_completion_coursename_errors_df.createOrReplaceTempView("raw_docebo_course_completion_coursename_errors")
    #raw_docebo_course_completion_coursename_errors_df.show()

    #Combining duplicate records 
    finalInvalidDF = spark.sql("""select personid,coursename,credithours,coursecode,dshscode,completiondate,filename,filedate,ValidInd,ValidIndERR from
                                    raw_docebo_course_completion_valid_flag where ValidInd=0  
                                UNION 
                                select personid,coursename,credithours,coursecode,dshscode,completiondate,filename,filedate,ValidInd,ValidIndERR from 
                                  raw_docebo_course_completion_duplicate_errors where ValidInd = 0
                                UNION
                                select personid,coursename,credithours,coursecode,dshscode,completiondate,filename,filedate,ValidInd,ValidIndERR from 
                                   raw_docebo_course_completion_coursename_errors where ValidInd = 0""")
    finalInvalidDF.createOrReplaceTempView("finalInvalidDF")
    #finalInvalidDF.show()

    ## valid records process it to training history table
    spark.sql("select * from raw_docebo_course_completion_coursename_errors where ValidInd=1" ).createOrReplaceTempView("raw_ds_course_completions")

    ## Combining coursecatalog  and completion details   
    docebocompletionsdf = spark.sql("""select distinct sc.personid ,sc.coursename,sc.completiondate,tc.credithours,
                                tc.trainingprogramtype,tc.trainingprogramcode,tc.courseid,'Online' as coursetype,tc.courselanguage ,tc.dshscourseid,
                                'NA' as instructorname, 'NA' as instructorid,'DOCEBO' as trainingsource,sc.filedate,sc.filename 
                                from raw_ds_course_completions sc left join coursecatalog tc on trim(lower(tc.courseid)) = trim(lower(sc.coursecode))""")

    print ("Valid records: {0}".format(docebocompletionsdf.count()))

    docebocompletionsdf.createOrReplaceTempView("docebocompletionsdf")
    #docebocompletionsdf.show()

    ## creating DynamicFrame for valid indicator records to insert into training history table 
    traininghistorydf = DynamicFrame.fromDF(docebocompletionsdf, glueContext, "traininghistorydf")

    # Script generated for node Apply Mapping
    ApplyMapping_node1646956720451 = ApplyMapping.apply(
        frame=traininghistorydf,
        mappings=[
            ("personid", "long", "personid", "long"),
            ("coursename", "string", "coursename", "string"),
            ("completiondate", "date", "completeddate", "date"),
            ("credithours", "string", "credithours", "double"),
            ("trainingprogramtype", "string", "trainingprogramtype", "string"),
            ("trainingprogramcode", "string", "trainingprogramcode", "long"),
            ("courseid", "string", "courseid", "string"),
            ("coursetype", "string", "coursetype", "string"),
            ("courselanguage", "string", "courselanguage", "string"),
            ("instructorname", "string", "instructorname", "string"),
            ("instructorid", "string", "instructorid", "string"),
            ("trainingsource", "string", "trainingsource", "string"),
            ("filedate", "timestamp", "filedate", "timestamp"),
            ("dshscourseid", "string", "dshscourseid", "string"),
            ("filename", "string", "filename", "string"),
        ],
        transformation_ctx="ApplyMapping_node1646956720451",
    )

    selectFields_raw_trainghistory = SelectFields.apply(
        frame=ApplyMapping_node1646956720451,
        paths=[
            "personid",
            "completeddate",
            "credithours",
            "coursename",
            "courseid",
            "coursetype",
            "courselanguage",
            "trainingprogramcode",
            "trainingprogramtype",
            "instructorname",
            "instructorid",
            "trainingsource",
            "filedate",
            "dshscourseid",
            "filename"
        ],
        transformation_ctx="selectFields_raw_trainghistory",
    )

    dyf_dropNullfields = DropNullFields.apply(frame = selectFields_raw_trainghistory)

    #Script generated for node PostgreSQL
    glueContext.write_dynamic_frame.from_catalog(
        frame=dyf_dropNullfields,
        database=catalog_database,
        table_name=catalog_table_prefix+"_raw_traininghistory"
    )
    #If invalid records found 
    if(finalInvalidDF.count() > 0):
        print("Found Invalid records")
        ## used to generate csv file invalid records from source file into s3 outbound folder
        outboundDF = finalInvalidDF.withColumnRenamed("completiondate","Completion Date")\
                            .withColumnRenamed("personid","Person ID")\
                            .withColumnRenamed("coursename","Course Name")\
                            .withColumnRenamed("credithours","credithours")\
                            .withColumnRenamed("coursecode","Course Code")\
                            .withColumnRenamed("dshscode","DSHS Code")\
                            .withColumnRenamed("ValidIndERR","Error Reason")\
                            .withColumnRenamed("filedate","File Date")\
                            .withColumnRenamed("status","Status")\
                            .withColumnRenamed("filename","Filename")\
                            .drop(col("ValidInd"))


        pandas_df = outboundDF.toPandas()

        suffix = outboundDF.first()["Filename"]
        pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/docebo/raw_to_raw_traininghistory_error_"+suffix, header = True, index = None, quotechar= '"', encoding ='utf-8', sep =',',quoting = csv.QUOTE_ALL)
        print(suffix)
        print ("Invalid records: {0}".format(finalInvalidDF.count()))

        # Adding to traininghistory logs
        finalInvalidDF.createOrReplaceTempView("finalInvalidDF")
        errordf = spark.sql("select personid,coursecode as courseid,dshscode as dshscourseid,cast(credithours as double) as credithours,coursename,completiondate as completeddate, 'NA' as instructorname, 'NA' as instructorid,'DOCEBO' as trainingsource,ValidIndERR as error_message,filename, filedate from finalInvalidDF")
        errorcdf = DynamicFrame.fromDF(errordf, glueContext, "historydf")

        glueContext.write_dynamic_frame.from_catalog(
        frame = errorcdf,
        database = catalog_database,
        table_name = catalog_table_prefix+"_logs_traininghistorylog",
        )

    print("Insert an entry into the log table")
    max_filedate = datetime.now()
    url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
    properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
    #max_filedate = raw_docebo_completion_df.max()['filedate']
    logs_data = [[ max_filedate, "glue-docebo-coursecompletions-raw-to-raw-traininghistory", "1" ]] 		 
    logs_columns = ['lastprocesseddate', 'processname','success'] 		 
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
    mode = 'append'  		 
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)

else:
    print("Data has already processed or no new data in the source table.")

print("****************Job execution completed*******************")

job.commit()