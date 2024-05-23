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
S3_BUCKET = s3_secrets['fileexchange']

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

mode = "append"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,
              "driver": "org.postgresql.Driver"}

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

#Capturing all the transcript corrections
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_raw_transcriptcorrections",
    transformation_ctx = "raw_transcriptcorrections").toDF().createOrReplaceTempView("raw_transcriptcorrections")

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
    table_name=catalog_table_prefix+"_prod_instructor",
).toDF().createOrReplaceTempView("instructor")

glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_coursecatalog",
).toDF().createOrReplaceTempView("coursecatalog")

ds1 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed", transformation_ctx = "datasource1")
logslastprocessed = ds1.toDF().createOrReplaceTempView("vwlogslastprocessed")



#Extracted the data from Database
raw_transcriptcorrections_df = spark.sql(f"""SELECT * FROM raw_transcriptcorrections WHERE filedate >
                                                (SELECT CASE WHEN MAX(lastprocesseddate) IS NULL THEN (current_date-1) ELSE MAX(lastprocesseddate)
                                                END AS MAXPROCESSDATE FROM vwlogslastprocessed
                                                WHERE processname='glue-transcript-corrections-raw-to-raw-traininghistory' AND success='1')""")

       
raw_transcriptcorrections_df.createOrReplaceTempView("raw_transcriptcorrections")
#raw_transcriptcorrections_df.show()
print ("Total records from raw : {0}".format(raw_transcriptcorrections_df.count()))
if(raw_transcriptcorrections_df.count() > 0):
    print("New file is processing") 

    ## Identify and flagging valid and invalid records if personid not found in prod person table
    raw_transcriptcorrections_valid_flag_df_1 = spark.sql("""select ROW_NUMBER() OVER (partition by ds.personid,ds.courseid,ds.coursename,ds.completeddate, ds.filename ORDER BY ds.personid,ds.courseid,ds.coursename,ds.completeddate, ds.filename) AS row_number,ds.personid,ds.courseid,ds.coursename,ds.dshscourseid,ds.credithours,ds.completeddate,ds.instructorid,lower(ds.instructor) as instructor,
    ds.trainingsource,ds.filename,ds.filedate,pr.personid as prod_personid, c.trainingprogramcode, c.trainingprogramtype as trainingprogramtype,left(SUBSTRING(ds.courseid, LENGTH(ds.courseid) - 6),3) as coursetype,c.courselanguage,
    lower(concat(i.firstname,' ',i.lastname)) as prod_instructorname, i.dshsinstructorid as prod_instructorid,
                    CASE WHEN pr.personid is null or completeddate > current_date or ((ds.instructorid is null or ds.instructor is null or i.instructorid is null or (ds.instructorid<>i.dshsinstructorid) )and left(SUBSTRING(ds.courseid, LENGTH(ds.courseid) - 6),3)<> 'ONL' )or (lower(ds.instructor)<>lower(concat(i.firstname,' ',i.lastname)))  or c.courseid is null THEN 0 ELSE 1 END IsValid
              from raw_transcriptcorrections ds left join prodperson pr on ds.personid = pr.personid
              left join instructor i on ds.instructorid=i.dshsinstructorid or lower(ds.instructor)=lower(concat(i.firstname,' ',i.lastname))
              left join coursecatalog c on ds.courseid=c.courseid""")
    raw_transcriptcorrections_valid_flag_df_1.createOrReplaceTempView("raw_transcriptcorrections_valid_flag_1")

    raw_transcriptcorrections_valid_flag_df=spark.sql("""Select ds.personid,ds.courseid,ds.coursename,ds.dshscourseid,ds.credithours,ds.completeddate,ds.instructorid, ds.instructor,ds.trainingsource, ds.filename,ds.filedate, prod_personid,trainingprogramcode,trainingprogramtype,coursetype,courselanguage,prod_instructorname,prod_instructorid,IsValid from raw_transcriptcorrections_valid_flag_1 ds where row_number=1""")
    raw_transcriptcorrections_valid_flag_df.createOrReplaceTempView("raw_transcriptcorrections_valid_flag")


    raw_transcriptcorrections_valid_flag_df = raw_transcriptcorrections_valid_flag_df.withColumn("ValidErr", when(col("prod_personid").isNull(),"Person ID does not exist").otherwise(""))

    raw_transcriptcorrections_valid_flag_df = raw_transcriptcorrections_valid_flag_df.withColumn("ValidErr", when(col("completeddate")> datetime.now(), concat(col("ValidErr"), when(col("ValidErr")=="",lit("Completion date is in future")).otherwise(lit(", Completion date is in future")))).otherwise(col("ValidErr")))

    raw_transcriptcorrections_valid_flag_df = raw_transcriptcorrections_valid_flag_df.withColumn("ValidErr", when(col("trainingprogramcode").isNull(), concat(col("ValidErr"), when(col("ValidErr")=="",lit("Course ID does not exist")).otherwise(lit(", Course ID does not exist")))).otherwise(col("ValidErr")))

    raw_transcriptcorrections_valid_flag_df = raw_transcriptcorrections_valid_flag_df.withColumn(
        "ValidErr",
        when(
            (col("prod_instructorid").isNull() & (col("coursetype")=='ILT')) | (col("instructorid").isNotNull() & (col("prod_instructorid") != col("instructorid"))),
            concat(col("ValidErr"), when(col("ValidErr")=="",lit("Instructor ID does not exist")).otherwise(lit(", Instructor ID does not exist")))
        ).otherwise(col("ValidErr")))
    raw_transcriptcorrections_valid_flag_df = raw_transcriptcorrections_valid_flag_df.withColumn(
        "ValidErr",
        when(
            (col("prod_instructorname") != col("instructor")) | col("prod_instructorname").isNull(),
            concat(col("ValidErr"),when(col("ValidErr")=="",lit("Instructor Name does not exist")).otherwise(lit(", Instructor Name does not exist")))
        ).otherwise(col("ValidErr")))

        

    #Filtering invalid records
    finalInvalidDF= raw_transcriptcorrections_valid_flag_df.filter(raw_transcriptcorrections_valid_flag_df["isvalid"] ==0)
    print(finalInvalidDF.schema)
    ## Valid records  
    Valid_df= raw_transcriptcorrections_valid_flag_df.filter(raw_transcriptcorrections_valid_flag_df["isvalid"] ==1) 
    Valid_df=Valid_df.withColumn("instructorid",when(col("coursetype")!= "ILT","NA").otherwise(col("instructorid")))
    Valid_df=Valid_df.withColumn("instructor",when(col("coursetype")!= "ILT","NA").otherwise(col("instructor")))

    print ("Valid records: {0}".format(Valid_df.count()))

    Valid_df.createOrReplaceTempView("Valid_df")
    #Valid_df.show()

    ## creating DynamicFrame for valid indicator records to insert into training history table 
    traininghistorydf = DynamicFrame.fromDF(Valid_df, glueContext, "traininghistorydf")

    # Script generated for node Apply Mapping
    ApplyMapping_node1646956720451 = ApplyMapping.apply(
        frame=traininghistorydf,
        mappings=[
            ("personid", "long", "personid", "long"),
            ("coursename", "string", "coursename", "string"),
            ("completeddate", "date", "completeddate", "date"),
            ("credithours", "double", "credithours", "double"),
            ("trainingprogramtype", "string", "trainingprogramtype", "string"),
            ("trainingprogramcode", "string", "trainingprogramcode", "long"),
            ("courseid", "string", "courseid", "string"),
            ("coursetype", "string", "coursetype", "string"),
            ("courselanguage", "string", "courselanguage", "string"),
            ("instructor", "string", "instructorname", "string"),
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
        outboundDF=finalInvalidDF
        ## used to generate csv file invalid records from source file into s3 outbound folder
        outboundDF = outboundDF.withColumnRenamed("completeddate","Completion Date")\
                            .withColumnRenamed("personid","Person ID")\
                            .withColumnRenamed("coursename","Course Name")\
                            .withColumnRenamed("credithours","credithours")\
                            .withColumnRenamed("courseid","Course ID")\
                            .withColumnRenamed("dshscourseid","DSHS Code")\
                            .withColumnRenamed("ValidErr","Error Reason")\
                            .withColumnRenamed("filedate","File Date")\
                            .withColumnRenamed("status","Status")\
                            .withColumnRenamed("filename","Filename")\
                            .drop(col("IsValid"))


        pandas_df = outboundDF.toPandas()

        suffix = outboundDF.first()["File Date"].strftime("%Y-%m-%d %H:%M:%S")
        pandas_df.to_csv("s3://"+S3_BUCKET+"/transcripts/corrections/errors/raw_to_raw_error_transcriptcorrections_"+suffix, header = True, index = None, quotechar= '"', encoding ='utf-8', sep =',',quoting = csv.QUOTE_ALL)
        print(suffix)
        print ("Invalid records: {0}".format(finalInvalidDF.count()))

        # Adding to traininghistory logs
        finalInvalidDF.createOrReplaceTempView("finalInvalidDF")
        #print(finalInvalidDF.schema)
        errordf = spark.sql("select personid,courseid as courseid,cast(trainingprogramcode as bigint),coursetype,courselanguage,dshscourseid,cast(credithours as double) as credithours,coursename,completeddate as completeddate,case when instructor is null and coursetype<>'ILT' then 'NA' else instructor end as instructorname, case when instructorid is null and coursetype<>'ILT' then 'NA' else instructorid end as instructorid,trainingsource,ValidErr as error_message,filename, filedate from finalInvalidDF")
        errorcdf= DynamicFrame.fromDF(errordf, glueContext, "historydf")

        glueContext.write_dynamic_frame.from_catalog(
        frame = errorcdf,
        database = catalog_database,
        table_name = catalog_table_prefix+"_logs_traininghistorylog",
        )
    print("Insert an entry into the log table")
    max_filedate = raw_transcriptcorrections_valid_flag_df.orderBy(desc("filedate")).limit(1).first()["filedate"]
    logs_data = [[max_filedate, "glue-transcript-corrections-raw-to-raw-traininghistory", "1"]]
    logs_columns = ['lastprocesseddate', 'processname','success']
    logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
    logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)
else:
    print("No new records found for processing")
print("****************Job execution completed*******************")

job.commit()
