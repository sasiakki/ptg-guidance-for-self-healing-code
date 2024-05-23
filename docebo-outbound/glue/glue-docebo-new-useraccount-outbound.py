import sys
from awsglue.transforms import *
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col,current_date,coalesce,concat,rank,concat_ws,when,collect_set,lit,to_date,date_format,initcap,lower,upper, rand, floor, current_timestamp, regexp_replace, to_timestamp, length
from pyspark.sql.window import Window
from awsglue.dynamicframe import DynamicFrame
import pandas
from datetime import datetime
import boto3
import json
from awsglue.utils import getResolvedOptions

#Default JOB arguments
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

#Capturing the current date to append to filename
today = datetime.now()
suffix = today.strftime("%m_%d_%Y")
suffix_timestamp = today.strftime("%m_%d_%Y_%H_%M_%S")

#Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')


#Accessing the secrets value for S3 Bucket
s3response_docebo = secretsmangerclient.get_secret_value(
    SecretId= environment_type+'/b2bds/s3_docebo'
)

s3_secrets_docebo = json.loads(s3response_docebo['SecretString'])
S3_BUCKET_docebo = s3_secrets_docebo['datafeeds']
S3_BUCKET_docebo_outbound = s3_secrets_docebo['outbound']

# Reading files from s3 and sorting it by last modified date to read only the earliest file
s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET_docebo+'')

#Capture current timestamp to identify incrementals
currentdatetime = datetime.now()

#Capturing lastprocessed datetime from logs.lastprocessed
lastprocessed_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_logs_lastprocessed").toDF()
lastprocessed_table_name=catalog_table_prefix+"_logs_lastprocessed"

#Capturing person demographic
person_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_person").toDF()

#Captruting trainingrequirement
trainingrequirement_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_trainingrequirement").toDF()

#Captruting employmentrelationship
employmentrelationship_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_employmentrelationship").toDF()

#Captruting employer info
employer_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_employer").toDF()

#Captruting employer trust info
employer_trust_df= glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_prod_employertrust").toDF()

#Captruting languages
raw_languages_df = glueContext.create_dynamic_frame.from_catalog(database=catalog_database, table_name=catalog_table_prefix+"_raw_languages").toDF()


# Registering the tempview for ro identify the delta users based on trainingrequirement and domographic information

lastprocessed_df.createOrReplaceTempView("lastprocessed")

person_df.createOrReplaceTempView("person")

trainingrequirement_df.createOrReplaceTempView("trainingrequirement")

employmentrelationship_df.createOrReplaceTempView("employmentrelationship")

delta_personids = spark.sql("""SELECT * FROM person WHERE recordcreateddate > (SELECT MAX(lastprocesseddate) from lastprocessed WHERE processname = 'docebo-new-user-data-outbound' AND success = '1')""")

employer_trust_select = employer_trust_df.select(col("employerid"),col("trust"))

employer_select = employer_df.select(col("employerid"),col("employername"))

employmentrelationship_select = employmentrelationship_df.filter(col("role") == "CARE").filter(col("createdby")!="ZenithLegacy").filter(col("empstatus") == "Active").select(col("employerid").alias("employer_id"),col("empstatus"),col("personid"))

trust_current_employer_trust = employer_select.join(employer_trust_select,employer_select.employerid == employer_trust_select.employerid,"leftouter").filter(col("trust") == "TP").drop(employer_trust_select.employerid).select(col("employerid"),col("employername"))

current_employer= trust_current_employer_trust.join(employmentrelationship_select,trust_current_employer_trust.employerid == employmentrelationship_select.employer_id,"leftouter").groupBy("personid").agg(concat_ws(";" , collect_set("employername")).alias("Current Employer"),concat_ws(",",collect_set(when(coalesce(col("employer_id"),lit(0)).isin(["103","426"]),"IP").otherwise("AP"))).alias("providertype")).select(col("personid").alias("personid"),col("Current Employer"), col("providertype"))

#
person_df_select = delta_personids.select(col("personid"),upper(col("firstname")).alias("firstname"),upper(col("middlename")).alias("middlename"),upper(col("lastname")).alias("lastname"),lower(col("email1")).alias("email1"),lower(col("email2")).alias("email2"),col("homephone"),col("mobilephone"),col("language").alias("preferedlanguage"),col("status").alias("employment_status"), col("status").alias("person_status"),col("exempt"),col("type"),col("workercategory"),col("ahcas_eligible"),col("trainingstatus"),col("mailingstreet1"),col("mailingstreet2"),col("mailingcity"),col("mailingstate"),col("mailingzip"),col("dshsid"),col("cdwaid"),col("sfcontactid"),col("recordmodifieddate"),col("recordcreateddate"))

person_df_select = person_df_select.select([when(col(c)=="",None).otherwise(col(c)).alias(c) for c in person_df_select.columns])

person_df_select = person_df_select.withColumn("exempt",when(col("exempt") == 'false', 0).otherwise(1))\
.withColumn("ahcas_eligible_update",when((col("ahcas_eligible").isNull()), False).otherwise(col("ahcas_eligible")))\
.withColumn("email1", coalesce(col("email1"), concat(col("personid").cast("string"), lit("@myseiubenefits.org"))))\
.withColumn('password', (concat(lit("Learn"), floor((rand() * (1000000000))).cast("int"))))\
.withColumn("homephone",when(col("homephone").isNull(),"").otherwise(concat(col("homephone").substr(2,3),lit("-"),col("homephone").substr(5,3),lit("-"),col("homephone").substr(8,4))))\
.withColumn("mobilephone",when(col("mobilephone").isNull(),"").otherwise(concat(col("mobilephone").substr(2,3),lit("-"),col("mobilephone").substr(5,3),lit("-"),col("mobilephone").substr(8,4))))\
.withColumn("Force Password Change",when(col("recordmodifieddate") ==  ("recordcreateddate"), '1').otherwise('0'))\
.withColumn("Level", lit("User"))\
.withColumn("Branch Code",lit("DS-CG"))\
.withColumn("trainingstatus",when(lower(col("trainingstatus")) == 'non-compliant','Non-Compliant').when(lower(col("trainingstatus")) == 'compliant','Compliant').otherwise(col("trainingstatus")))\
.withColumn("TimeZone",lit("America/Los_Angeles"))\
.withColumn("language",lit("English"))\
.withColumn("Force Password Change",lit("1"))\
.drop(col("recordcreateddate"))\
.drop(col("recordmodifieddate"))
                                    
raw_languages_df_select = raw_languages_df.select(col("code"),col("value"))
                                    
person_df_select = person_df_select.join(raw_languages_df_select,person_df_select.preferedlanguage == raw_languages_df_select.code,"leftouter").drop(raw_languages_df_select.code)

person_df_select = person_df_select.withColumn("preferedlanguage",coalesce(raw_languages_df.value,when(person_df_select.preferedlanguage == 'EN', 'English').when(person_df_select.preferedlanguage.isNull(), 'English').otherwise(person_df_select.preferedlanguage)))


current_emp_result = person_df_select.join(current_employer,person_df_select.personid == current_employer.personid,"leftouter").drop(current_employer.personid)

trainingrequirement_select = trainingrequirement_df.select(col('trainingprogramcode'),col("trainingprogram"),col("trainingid"),col("completeddate"),col("trackingdate"),col("duedate"),col("duedateextension"),col("requiredhours"),col("earnedhours"),col("transferredhours"),col("status").alias("trainingrequirement_status"),col("isrequired"),col("archived"),col("personid"))\
                                .filter(col("status") == "active")\
                                .filter(col("isrequired") == "true")\
                                .filter(col("archived").isNull())\
                                .na.fill(value=0,subset=["earnedhours","transferredhours"])

training_ranking_window = Window.partitionBy(col("personid")).orderBy(coalesce(to_date(col("trackingdate"), "yyyy-mm-dd"),current_date()).desc())

trainingrequirement_active = trainingrequirement_select.select(col('trainingprogramcode'),col("trainingprogram"),col("trainingid"),col("completeddate"),col("trackingdate"),col("trackingdate").alias("futuretrackingdate"),col("duedate"),col("duedateextension"),col("requiredhours"),col("earnedhours"),col("transferredhours"),col("trainingrequirement_status"),col("personid"),rank().over(training_ranking_window).alias("training_rank")).filter(col("training_rank") == 1)\
                                    .withColumn("trackingdate", regexp_replace(date_format(to_date("trackingdate", "yyyy-mm-dd"),"MM/dd/yyyy"),"-","/"))\
                                    .withColumn("duedate", regexp_replace(date_format(to_date("duedate", "yyyy-mm-dd"),"MM/dd/yyyy"),"-","/"))\
                                    .withColumn("duedateextension", regexp_replace(date_format(to_date("duedateextension", "yyyy-mm-dd"),"MM/dd/yyyy"),"-","/"))\
                                    .withColumn("completeddate", regexp_replace(date_format(to_date("completeddate", "yyyy-mm-dd"),"MM/dd/yyyy"),"-","/"))\
                                    .drop(col("training_rank"))


new_userinfo_df = current_emp_result.join(trainingrequirement_active,current_emp_result.personid == trainingrequirement_active.personid,"leftouter").drop(trainingrequirement_active.personid)

new_userinfo_df = new_userinfo_df.withColumn("Active", when(((col("person_status") == 'Terminated') & (col("trainingrequirement_status") == 'active')),0).when((col("person_status") == 'Terminated') & (col("trainingrequirement_status") == 'closed'),0).when((col("person_status") == 'Terminated' ) & (col("trainingrequirement_status").isNull()),0).otherwise(1))\

new_userinfo_df = new_userinfo_df.withColumn("futuretrackingdate",when( col("futuretrackingdate") > current_timestamp(),1).when( col("futuretrackingdate") <= current_timestamp(),0 ).when( length("futuretrackingdate") == 0,0 ).otherwise(0) )\
    .withColumn("Required Hours", coalesce(col("requiredhours"),lit(0.0)))\
    .withColumn("Earned Hours", coalesce(col("earnedhours"),lit(0.0)))\
    .withColumn("Transferred Hours", coalesce(col("transferredhours"),lit(0.0)))\
    .withColumn("Remaining Hours", coalesce(col("requiredhours")-(col("earnedhours")+col("transferredhours")),lit(0.0)))\


new_userinfo_df = new_userinfo_df.withColumnRenamed('status',"Employment Status")\
.drop(col("value"))

outbound_new_user_info_df = new_userinfo_df.select( col("personid").alias("PersonID"), col("personid").alias("Username"), col("firstname").alias("First Name"),col("middlename").alias("Middle Name"),col("lastname").alias("Last Name"),col("password").alias("Password"), col("email1").alias("Email"), col("email2").alias("Email2"), col("TimeZone"), col("Active"), col("Level"), col("language"), col("Branch Code"), col("Force Password Change"), col("dshsid"), col("cdwaid"), col("sfcontactid").alias("sfid"), col("homephone").alias("Home Phone"), col("mobilephone").alias("Mobile Phone"), col("mailingstreet1").alias("Mailing Street 1"), col("mailingstreet2").alias("Mailing Street 2"),col("mailingcity").alias("Mailing City"), col("mailingstate").alias("Mailing State"), col("mailingzip").alias("Mailing Zip"), col("workercategory").alias("Worker Category"), col("trainingstatus").alias("Training Status"), col("employment_status").alias("Employment Status"), when( col("providertype").isin(['AP,IP', 'IP,AP']),"DP").otherwise(col("providertype")).alias("Provider Type"), col("Current Employer").alias("Current Employer(s)"), col("exempt").alias("Exempt Status"), col("preferedlanguage").alias("Preferred Language"), col("trainingid").alias("TrainingID"), col("trainingprogram").alias("Active Training Requirement"), col("trackingdate").alias("Tracking Date"), col("ahcas_eligible").alias("AHCAS Eligible"), col("Required Hours"), col("Earned Hours"),col("Transferred Hours"), col("Remaining Hours"), col("futuretrackingdate").alias("Future Trackingdate"), col("duedate").alias("Due Date"), col("duedateextension").alias("Due Date Extension"), col("completeddate").alias("Completed Date"))


new_user_info_df = outbound_new_user_info_df.distinct()

new_user_info_pdf = new_user_info_df.toPandas()

#New Useraccount
#new_user_info_pdf.to_csv("s3://"+S3_BUCKET+"/Outbound/docebo/Learner-Training-NewUsers-"+suffix+".csv", header=True, index=None, sep='|')
new_user_info_pdf.to_csv("s3://"+S3_BUCKET_docebo+"/toprocess/NewLearner/NewLearner.csv", header=True, index=None, sep=',')
new_user_info_pdf.to_csv("s3://"+S3_BUCKET_docebo_outbound+"/Outbound/docebo/NewLearner/NewLearner-"+suffix_timestamp+".csv", header=True, index=None, sep=',')

#WRITE a record with process/execution time to logs.lastprocessed table
#Create Dynamic Frame to log lastprocessed table

dfi = spark.createDataFrame([("docebo-new-user-data-outbound",currentdatetime,"1")],schema=["processname", "lastprocesseddate", "success"])

PostgreSQLtable_node2 = DynamicFrame.fromDF(dfi, glueContext, "PostgreSQLtable_node2")

ApplyMapping_node2 = ApplyMapping.apply(frame=PostgreSQLtable_node2,mappings=[("processname", "string", "processname", "string"),("lastprocesseddate", "timestamp","lastprocesseddate", "timestamp"),("success", "string", "success", "string")],transformation_ctx="ApplyMapping_node2")

#Write to postgresql logs.lastprocessed table of the success
PostgreSQLtable_node3 = glueContext.write_dynamic_frame.from_catalog(frame=ApplyMapping_node2,database=catalog_database,table_name=lastprocessed_table_name,transformation_ctx="PostgreSQLtable_node3")


job.commit()