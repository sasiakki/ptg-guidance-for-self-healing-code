import sys
import boto3
import json
from datetime import datetime,date
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from awsglue.utils import getResolvedOptions



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

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


# Setting the timeParserPolicy as legacy for handling multiple types of date formats received in smartsheet_course_completion responses  
spark.sql("set spark.sql.legacy.timeParserPolicy=LEGACY")


print("****************Starting Job execution*******************")

#doceboILT course completions table with only delta records
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_raw_doceboilt_course_completion",
).toDF().filter("isdelta == 'true'").createOrReplaceTempView("raw_doceboilt_course_completion")

#Script for node PostgreSQL of coursecatalog
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_coursecatalog",
).toDF().createOrReplaceTempView("coursecatalog")

# Script generated for node PostgreSQL
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_prod_person",).toDF().createOrReplaceTempView("person")
# Script for node PostgreSQL of instructor
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name= catalog_table_prefix+"_prod_instructor",
).toDF().createOrReplaceTempView("instructor")

#Capturing lastprocessed datetime from logs.lastprocessed
## B2BDS-1340: Access the lastprocessed log table and create a DF for Delta Detection purpose
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, 
    table_name=catalog_table_prefix+"_logs_lastprocessed"
 ).toDF()
lastprocessed_df.createOrReplaceTempView("vwlogslastprocessed")

raw_doceboilt_completion_df = spark.sql("SELECT COUNT(*) as countval FROM raw_doceboilt_course_completion")
print (raw_doceboilt_completion_df.first()["countval"])
# Removing the duplicate course completions received from multiple files and only preserving completions in the earliest file date
raw_doceboilt_completion_df = spark.sql("with doceboILT_raw as (select username,firstname,lastname,trainingid,coursename,coursecode,credits,dshscode,sessioninstructor,sessionname,eventinstructor,TO_DATE(completiondate, 'yyyy-MM-dd') AS completiondate,filename,filedate, ROW_NUMBER () OVER ( PARTITION BY username, coursename ORDER BY completiondate) courserank from raw_doceboilt_course_completion dc WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory' AND success='1') order by dc.coursename desc) select * from doceboILT_raw where courserank = 1")

print ("Total records from raw_doceboilt_completion_df : {0}".format(raw_doceboilt_completion_df.count()))
if (raw_doceboilt_completion_df.count() > 0):
    raw_doceboilt_completion_df.createOrReplaceTempView("raw_doceboilt_completion")
     
    # Removing duplicate courses completions
    coursecatalog = spark.sql( """with coursecatalog as (select *, ROW_NUMBER () OVER ( PARTITION BY curr.coursename, curr.courselanguage,curr.trainingprogramcode ORDER BY curr.coursetype ASC ) courserank from coursecatalog curr) select  coursename ,credithours ,trainingprogramtype, trainingprogramcode, coursetype, courselanguage,courseversion,courseid,dshscourseid from coursecatalog where courserank = 1 """)
    
    coursecatalog.createOrReplaceTempView("coursecatalog")
    
    #print ("Total records from coursecatalog : {0}".format(coursecatalog.count()))
    
    # Capturing only the active instuctors from the instructor table
    instructor = spark.sql("""select distinct trim(concat(trim(firstname),' ',trim(lastname))) as instructorname , dshsinstructorid  as instructorid from instructor""")
    
    instructor.createOrReplaceTempView("instructor")  

   # print ("Total records from instructor : {0}".format(instructor.count()))
    ## Identify and flagging duplicate courses completions
    raw_doceboilt_completion_duplicate = spark.sql("""with doceboILT_raw as (select username,firstname,lastname,trainingid,coursename,coursecode,credits,dshscode,sessioninstructor,sessionname,eventinstructor,TO_DATE(completiondate, 'yyyy-MM-dd') AS completiondate,filename,filedate, ROW_NUMBER () OVER ( PARTITION BY username,coursename,coursecode ORDER BY completiondate) courserank from raw_doceboilt_course_completion dc WHERE recordmodifieddate > (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate) END AS MAXPROCESSDATE FROM vwlogslastprocessed WHERE processname='glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory' AND success='1') order by dc.coursename desc) select * from doceboILT_raw where courserank > 1""")
    
    raw_doceboilt_completion_duplicate.createOrReplaceTempView("raw_doceboilt_completion_duplicate")
    
    #print ("Total records from raw_doceboilt_completion_duplicate : {0}".format(raw_doceboilt_completion_duplicate.count()))
    
    raw_doceboilt_completion_duplicate = spark.sql("""select *, 'Duplicate course completion' as ValidIndERR,0 as ValidInd,sessioninstructor from raw_doceboilt_completion_duplicate""")
    
    raw_doceboilt_completion_duplicate.createOrReplaceTempView("raw_doceboilt_completion_duplicate")
    
    #print ("Total records from raw_doceboilt_completion_duplicate_2 : {0}".format(raw_doceboilt_completion_duplicate.count()))


    ## Identify and flagging valid and invalid records if personid not found in prod person table
    raw_doceboilt_username_completiondate_valid_flag = spark.sql("""select cs.*, 
                    CASE WHEN pr.personid is null or cs.completiondate > current_date THEN 0 ELSE 1 END ValidInd,
                    CASE 
                     WHEN pr.personid is null THEN 'Personid is not Valid'
                     WHEN cs.completiondate > current_date THEN 'Completion Date is in the Future'
                    END ValidIndERR
                    from raw_doceboilt_completion cs left join person pr on trim(cs.username) = cast(pr.personid as string)""")
    
    raw_doceboilt_username_completiondate_valid_flag.createOrReplaceTempView("raw_doceboilt_username_completiondate_valid_flag")
    
    #print ("Total records from raw_doceboilt_username_completiondate_valid_flag : {0}".format(raw_doceboilt_username_completiondate_valid_flag.count()))

    ## identifying duplicate records based on learner_id,class_title getting earliest record and flagging valid and invalid records
    raw_doceboilt_completions_DuplicateCourseError = spark.sql("""select username,firstname,lastname,trainingid,coursecode,coursename,credits,dshscode,sessioninstructor,completiondate,filename,filedate,
                CASE WHEN completionsrank>1 then 'Course Completion is Redundant' end as ValidIndERR, 
                CASE WHEN completionsrank>1 then 0 else 1 end as ValidInd 
                from (select *, row_number() over (Partition by username,coursecode ORDER BY completiondate ASC ) completionsrank 
                from raw_doceboilt_username_completiondate_valid_flag where ValidInd=1) DS""")
    
    raw_doceboilt_completions_DuplicateCourseError.createOrReplaceTempView("raw_doceboilt_completions_DuplicateCourseError")
    #print ("Total records from raw_doceboilt_completions_DuplicateCourseError : {0}".format(raw_doceboilt_completions_DuplicateCourseError.count()))

    ## Filtering invalid class_title and flagging valid and invalid records
    raw_doceboilt_completions_DuplicateError = spark.sql("""select username,firstname,lastname,trainingid,coursecode,cs.coursename,credits,dshscode,cs.sessioninstructor,completiondate,filename,filedate,
                            CASE
                            WHEN tc.courseid is null then 'Courseid is not Valid'
                            WHEN ins.instructorname is null then 'Instructorname is not Valid' end as ValidIndERR, 
                            CASE WHEN tc.courseid is null or ins.instructorname is null then 0 else 1 end as ValidInd 
                            from raw_doceboilt_completions_DuplicateCourseError cs 
                            left join coursecatalog tc on cs.coursecode = tc.courseid 
                            left join instructor ins on lower(trim(ins.instructorname)) = lower(trim(cs.sessioninstructor)) where cs.ValidInd=1""")
    raw_doceboilt_completions_DuplicateError.createOrReplaceTempView("raw_doceboilt_completions_DuplicateError")
   # print ("Total records from raw_doceboilt_completions_DuplicateError : {0}".format(raw_doceboilt_completions_DuplicateError.count()))

    ## valid records process it to training history table
    raw_doceboilt_completions_DuplicateError_2 = spark.sql("select * from raw_doceboilt_completions_DuplicateError where ValidInd=1" )
    
    raw_doceboilt_completions_DuplicateError_2.createOrReplaceTempView("raw_doceboilt_completions")
   # print ("Total records from raw_doceboilt_completions : {0}".format(raw_doceboilt_completions_DuplicateError_2.count()))
    
    # Combining coursecatalog , instructor and completion details   
    doceboiltcompletionsdf = spark.sql("select distinct sc.username,sc.coursename ,completiondate,sc.credits,tc.trainingprogramtype,tc.trainingprogramcode,sc.coursecode ,tc.coursetype ,tc.courselanguage ,tc.dshscourseid, sc.sessioninstructor,ins.instructorid,sc.filedate,sc.filename,'DOCEBOILT' as trainingsource from raw_doceboilt_completions sc left join coursecatalog tc on sc.coursecode = tc.courseid left join instructor ins on lower(trim(ins.instructorname)) = lower(trim(sc.sessioninstructor))")

    #print ("Total records from doceboiltcompletionsdf_1 : {0}".format(doceboiltcompletionsdf.count()))
    # Coverting  spark dataframe to glue dynamic dataframe
    newdatasource = DynamicFrame.fromDF(doceboiltcompletionsdf, glueContext, "newdatasource")

    # Script generated for node Apply Mapping
    ApplyMapping_node1646956720451 = ApplyMapping.apply(
        frame= newdatasource,
        mappings=[
            ("username", "string", "personid", "long"),
            ("coursename", "string", "coursename", "string"),
            ("completiondate", "date", "completeddate", "date"),
            ("credits", "string", "credithours", "double"),
            ("trainingprogramtype", "string", "trainingprogramtype", "string"),
            ("trainingprogramcode", "string", "trainingprogramcode", "long"),
            ("coursecode", "string", "courseid", "string"),
            ("coursetype", "string", "coursetype", "string"),
            ("courselanguage", "string", "courselanguage", "string"),
            ("sessioninstructor", "string", "instructorname", "string"),
            ("instructorid", "string", "instructorid", "string"),
            ("trainingsource", "string", "trainingsource", "string"),
             ("filedate", "date", "filedate", "timestamp"),
             ("filename", "string", "filename", "string"),
              ("dshscourseid", "string", "dshscourseid", "string"),
        ],
        transformation_ctx="ApplyMapping_node1646956720451",
    )
    selectFields_raw_trainghistory = SelectFields.apply(
        frame=ApplyMapping_node1646956720451,
        paths=[
            "personid",
            "coursename",
            "courseid",
            "completeddate",
            "credithours",
            "trainingprogramcode",
            "trainingprogramtype",
            "courselanguage",
            "coursetype",
            "instructorname",
            "instructorid",
            "trainingsource",
            "filedate",
            "filename",
            "dshscourseid"
        ],
        transformation_ctx="selectFields_raw_trainghistory",
    )
    dyf_dropNullfields = DropNullFields.apply(frame = selectFields_raw_trainghistory)

    #Script for node PostgreSQL writing to raw.traininghistory
    glueContext.write_dynamic_frame.from_catalog(
        frame=dyf_dropNullfields,
        database = catalog_database,
        table_name= catalog_table_prefix+"_raw_traininghistory",
    )

    #Combining duplicate records 
    finalInvalidDF = spark.sql("""select username,firstname,lastname,trainingid,coursecode,coursename,credits,dshscode,sessioninstructor,completiondate,filename,filedate,ValidInd,uc.ValidIndERR from
                                raw_doceboilt_username_completiondate_valid_flag uc where ValidInd= 0 
                                UNION 
                                select username,firstname,lastname,trainingid,coursecode,coursename,credits,dshscode,sessioninstructor,completiondate,filename,filedate,ValidInd,dcdc.ValidIndERR from 
                                raw_doceboilt_completions_DuplicateCourseError dcdc where ValidInd = 0 
                                UNION 
                                select username,firstname,lastname,trainingid,coursecode,coursename,credits,dshscode,sessioninstructor,completiondate,filename,filedate,ValidInd,dcd.ValidIndERR from 
                                raw_doceboilt_completions_DuplicateError dcd where ValidInd = 0
                                UNION 
                                select username,firstname,lastname,trainingid,coursecode,coursename,credits,dshscode,sessioninstructor,completiondate,filename,filedate,ValidInd,cd.ValidIndERR from raw_doceboilt_completion_duplicate cd where ValidInd = 0""")

    #If invalid records found
   
    if(finalInvalidDF.count() > 0):
        #print ("Total records from finalInvalidDF : {0}".format(finalInvalidDF.count()))
        #print("Found Invalid records")
        ## used to generate csv file invalid records from source file into s3 outbound folder
        outboundDF = finalInvalidDF.withColumnRenamed("username","Username")\
                                   .withColumnRenamed("firstname","First Name")\
                                   .withColumnRenamed("lastname","Last Name")\
                                   .withColumnRenamed("trainingid","TrainingID")\
                                   .withColumnRenamed("coursename","Course Name")\
                                   .withColumnRenamed("coursecode","Course code")\
                                   .withColumnRenamed("credits","Credits (CEUs)")\
                                   .withColumnRenamed("dshscode","DSHS Code")\
                                   .withColumnRenamed("sessioninstructor","Instructor name")\
                                   .withColumnRenamed("completiondate","Completion Date")\
                                   .withColumnRenamed("ValidIndERR","error_message")\
                                    .drop(col("ValidInd"))


        pandas_df = outboundDF.toPandas()
        
        #Capturing the current date to append to filename
        file_date= datetime.now()
        suffix = file_date.strftime("%Y-%m-%d")
        pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/doceboilt/DoceboILT_raw_to_raw_traininghistory_error_"+ suffix+".csv", header=True, index=None, sep=',')
        print(suffix)
        print ("Invalid records: {0}".format(finalInvalidDF.count()))

        # Adding to traininghistory logs
        finalInvalidDF.createOrReplaceTempView("finalInvalidDF")
        errordf = spark.sql("select cast(username as bigint) personid,coursename,coursecode,dshscode,completiondate,CAST(credits AS DOUBLE) as credithours, sessioninstructor,'DOCEBOILT' as trainingsource,ValidIndERR,filename,filedate from finalInvalidDF")
        doceboilt_logs = DynamicFrame.fromDF(errordf, glueContext, "doceboilt_logs")
        
        #print ("Invalid records: {0}".format(doceboilt_logs.count()))
        
                #Apply Mapping to match the target table and datatype 
        doceboilt_raw_logs = ApplyMapping.apply(
                    frame=doceboilt_logs,
                    mappings=[
                        ("personid", "bigint", "personid", "bigint"),
                        ("trainingsource", "string", "trainingsource", "string"),
                        ("coursename", "string", "coursename", "string"),
                        ("coursecode", "string", "courseid", "string"),
                        ("credithours", "double", "credithours", "double"),
                        ("dshscode", "string", "dshscourseid", "string"),
                        ("sessioninstructor", "string", "instructorname", "string"),
                        ("completiondate", "date", "completeddate", "date"),
                        ("filename", "string", "filename", "string"),
                        ("filedate", "date", "filedate", "date"),
                        ("ValidIndERR", "string", "error_message", "string")
                    ],
                    transformation_ctx="doceboilt_raw_logs",
                )
            

        glueContext.write_dynamic_frame.from_catalog(
        frame = doceboilt_raw_logs,
        database = catalog_database,
        table_name = catalog_table_prefix+"_logs_traininghistorylog",
        )

    print("Insert an entry into the log table")
    max_filedate = datetime.now()
    url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
    properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
    #max_filedate = raw_docebo_completion_df.max()['filedate']
    logs_data = [[ max_filedate, "glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory", "1" ]] 		 
    logs_columns = ['lastprocesseddate', 'processname','success'] 		 
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns) 		 
    mode = 'append'  		 
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
else:
    print("Data has already processed or no new data in the source table.")

print("****************Job execution completed*******************")

job.commit()