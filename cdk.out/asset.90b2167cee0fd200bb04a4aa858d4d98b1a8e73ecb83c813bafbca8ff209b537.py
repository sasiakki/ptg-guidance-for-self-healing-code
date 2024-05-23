import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col,concat_ws,md5,row_number,when,lit
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.window import Window
import boto3
import json
import pandas
from datetime import datetime

# Default JOB arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


today = datetime.now()
suffix = today.strftime("%Y%m%d")

print(suffix)

args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_JSON['environment_type']

if environment_type == 'dev' :
    catalog_database = 'postgresrds'
    catalog_table_prefix = 'b2bdevdb'
else:
    catalog_database = 'seiubg-rds-b2bds'
    catalog_table_prefix = 'b2bds'

# Accessing the Secrets Manager from boto3 lib
secretsmangerclient = boto3.client('secretsmanager')

# Accessing the secrets target database
databaseresponse = secretsmangerclient.get_secret_value(
    SecretId=environment_type+'/b2bds/rds/system-pipelines'
)
database_secrets = json.loads(databaseresponse['SecretString'])

B2B_USER = database_secrets['username']
B2B_PASSWORD = database_secrets['password']
B2B_HOST = database_secrets['host']
B2B_PORT = database_secrets['port']
B2B_NAME = database_secrets['dbname']



# Captutre the current day DOH credentials data from raw.credential
credential_df = glueContext.create_dynamic_frame.from_catalog(database = catalog_database , table_name = catalog_table_prefix+"_raw_credential").toDF()

# Captutre the previous credentials data from raw.credential_delta table 
credential_delta_df = glueContext.create_dynamic_frame.from_catalog(database = catalog_database , table_name = catalog_table_prefix+"_raw_credential_delta").toDF()

# Captutre the OSPI Type credentials data from raw.credential_ospi table 
credential_ospi_df = glueContext.create_dynamic_frame.from_catalog(database = catalog_database , table_name = catalog_table_prefix+"_raw_credential_ospi").toDF()

logslastprocessed = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_lastprocessed").toDF()
logslastprocessed = logslastprocessed.createOrReplaceTempView("vwlogslastprocessed")

print('DOH-Credentials')
credential_df.printSchema();
credential_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794"})).show(10,truncate=False);

print('OSPI-Credentials')
credential_ospi_df.printSchema();
credential_ospi_df.where(col("credentialnumber").isin({"OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

print('Delta-Credentials')
credential_delta_df.printSchema();
credential_delta_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794"})).show(10,truncate=False);


# Create OSPI Temprory view for the data enrichment 
credential_ospi_df.createOrReplaceTempView("credential_ospi")
credential_ospi_df = spark.sql("""
                                select 
                                     cast(personid as long) as studentid
                                    ,credentialnumber
                                    ,CONCAT_WS(' ',lastname,firstname,middlename) as providernamedoh
                                    ,date_format(birthdate,"MM/dd/yyyy") as dateofbirth
                                    ,date_format(firstissuancedate,"MM/dd/yyyy") as firstissuancedate
                                    ,date_format(expirationdate,"MM/dd/yyyy") as expirationdate
                                    ,'OSPI' as credentialtype
                                    ,credentialstatus
                                    ,recordmodifieddate
                                    ,recordcreateddate
                                    ,filename
                                    ,cast(filedate as timestamp ) as filemodifieddate
                                from credential_ospi
                                where recordmodifieddate > (
                                select case when max(lastprocesseddate) is null then (current_date-1) 
                                       else max(lastprocesseddate)
                                       end as MAXPROCESSDATE
                                from vwlogslastprocessed 
                                where processname='glue-credentials-delta-processing' and success='1')""")

for column in [column for column in credential_df.columns if column not in credential_ospi_df.columns]:
    credential_ospi_df = credential_ospi_df.withColumn(column, lit(None))

# Combining the OSPI Type of credentials and DOH Credentials
if credential_ospi_df.count() != 0 : 
    print("OSPI credential record count:{0} ".format(credential_ospi_df.count()))
    credential_df = credential_df.unionByName(credential_ospi_df, allowMissingColumns=False)
    print('OSPI-Credentials - AFter Union')
    credential_ospi_df.printSchema();
    credential_ospi_df.where(col("credentialnumber").isin({"OSPI443620J", "OSPI516281C"})).show(10,truncate=False);


print('Credentials AFter Union')
credential_df.printSchema();
credential_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

print('Delta-Credentials')
credential_delta_df.printSchema();
credential_delta_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

# Removing all the empty spaces and "NULL" strings
credential_df = credential_df.select([when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c) for c in credential_df.columns])
credential_delta_df = credential_delta_df.select([when(col(c) == "", None).when(col(c) == "NULL", None).otherwise(col(c)).alias(c) for c in credential_delta_df.columns])


# Dropping the previously calculated MD5 Hash values for comparision
credential_df = credential_df.drop("hashidkey")
credential_delta_df = credential_delta_df.drop("hashidkey","newhashidkey","audit")

# Calculating the MD5 Hash values for comparision
credential_df = credential_df.withColumn("newhashidkey",md5(concat_ws("",col("taxid"),col("providernumber"),col("credentialnumber"),col("providernamedshs"),col("providernamedoh"),col("dateofbirth"),col("dateofhire"),col("limitedenglishproficiencyindicator"),col("firstissuancedate"),col("lastissuancedate"),col("expirationdate"),col("credentialtype"),col("credentialstatus"),col("lepprovisionalcredential"),col("lepprovisionalcredentialissuedate"),col("lepprovisionalcredentialexpirationdate"),col("actiontaken"),col("continuingeducationduedate"),col("longtermcareworkertype"),col("excludedlongtermcareworker"),col("paymentdate"),col("credentiallastdateofcontact"),col("preferredlanguage"),col("credentialstatusdate"),col("nctrainingcompletedate"),col("examscheduleddate"),col("examscheduledsitecode"),col("examscheduledsitename"),col("examtestertype"),col("examemailaddress"),col("examdtrecdschedtestdate"),col("phonenum"))))
credential_delta_df = credential_delta_df.withColumn("oldhashidkey",md5(concat_ws("",col("taxid"),col("providernumber"),col("credentialnumber"),col("providernamedshs"),col("providernamedoh"),col("dateofbirth"),col("dateofhire"),col("limitedenglishproficiencyindicator"),col("firstissuancedate"),col("lastissuancedate"),col("expirationdate"),col("credentialtype"),col("credentialstatus"),col("lepprovisionalcredential"),col("lepprovisionalcredentialissuedate"),col("lepprovisionalcredentialexpirationdate"),col("actiontaken"),col("continuingeducationduedate"),col("longtermcareworkertype"),col("excludedlongtermcareworker"),col("paymentdate"),col("credentiallastdateofcontact"),col("preferredlanguage"),col("credentialstatusdate"),col("nctrainingcompletedate"),col("examscheduleddate"),col("examscheduledsitecode"),col("examscheduledsitename"),col("examtestertype"),col("examemailaddress"),col("examdtrecdschedtestdate"),col("phonenum"))))


print('DOH-Credentials Before MD5 Hash values')
credential_df.printSchema();
credential_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

print('Delta-Credentials After MD5 Hash values')
credential_delta_df.printSchema();
credential_delta_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

# Creating the Temp Tables for credential and credential_delta tables
credential_df.createOrReplaceTempView("credential")
credential_delta_df.createOrReplaceTempView("credential_delta")


credential_clean_df = credential_df

credential_clean_df.printSchema();
credential_clean_df.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

# Creating the Temp Table for credential after the cleanup as credential_clean
credential_clean_df.createOrReplaceTempView("credential_clean")


#  Performing the LEFT Anti Join on credential_clean to captute the new credential records based on calculated hash keys
newandupdatedcredentialsdf = spark.sql("select cc.*, 'New' as audit from  credential_clean cc LEFT ANTI JOIN credential_delta dc on cc.newhashidkey == dc.oldhashidkey")

print('new and updated credentials df-Credentials')
newandupdatedcredentialsdf.printSchema();
newandupdatedcredentialsdf.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);


# Creating the Temp Table for new credential as credential_new
newandupdatedcredentialsdf.createOrReplaceTempView("credential_new")

# Performing the FULL OUTER JOIN on credential_clean and new credential to capture the audit records
resultdf = spark.sql("""
    select
     case WHEN cn.audit = 'New' and cn.credentialtype = 'OSPI' then cn.studentid ELSE dc.personid END AS personid
    ,case WHEN cn.audit = 'New' then cn.taxid ELSE dc.taxid END AS taxid
    ,case WHEN cn.audit = 'New' then cn.providernumber ELSE dc.providernumber END AS providernumber
    ,case WHEN cn.audit = 'New' then cn.credentialnumber ELSE dc.credentialnumber END AS credentialnumber
    ,case WHEN cn.audit = 'New' then cn.providernamedshs ELSE dc.providernamedshs END AS providernamedshs
    ,case WHEN cn.audit = 'New' then cn.providernamedoh ELSE dc.providernamedoh END AS providernamedoh
    ,case WHEN cn.audit = 'New' then cn.dateofbirth ELSE dc.dateofbirth END AS dateofbirth
    ,case WHEN cn.audit = 'New' then cn.dateofhire ELSE dc.dateofhire END AS dateofhire
    ,case WHEN cn.audit = 'New' then cn.limitedenglishproficiencyindicator ELSE dc.limitedenglishproficiencyindicator END AS limitedenglishproficiencyindicator
    ,case WHEN cn.audit = 'New' then cn.firstissuancedate ELSE dc.firstissuancedate END AS firstissuancedate
    ,case WHEN cn.audit = 'New' then cn.lastissuancedate ELSE dc.lastissuancedate END AS lastissuancedate
    ,case WHEN cn.audit = 'New' then cn.expirationdate ELSE dc.expirationdate END AS expirationdate
    ,case WHEN cn.audit = 'New' then cn.credentialtype ELSE dc.credentialtype END AS credentialtype
    ,case WHEN cn.audit = 'New' then cn.credentialstatus ELSE dc.credentialstatus END AS credentialstatus
    ,case WHEN cn.audit = 'New' then cn.lepprovisionalcredential ELSE dc.lepprovisionalcredential END AS lepprovisionalcredential
    ,case WHEN cn.audit = 'New' then cn.lepprovisionalcredentialissuedate ELSE dc.lepprovisionalcredentialissuedate END AS lepprovisionalcredentialissuedate
    ,case WHEN cn.audit = 'New' then cn.lepprovisionalcredentialexpirationdate ELSE dc.lepprovisionalcredentialexpirationdate END AS lepprovisionalcredentialexpirationdate
    ,case WHEN cn.audit = 'New' then cn.actiontaken ELSE dc.actiontaken END AS actiontaken
    ,case WHEN cn.audit = 'New' then cn.continuingeducationduedate ELSE dc.continuingeducationduedate END AS continuingeducationduedate
    ,case WHEN cn.audit = 'New' then cn.longtermcareworkertype ELSE dc.longtermcareworkertype END AS longtermcareworkertype
    ,case WHEN cn.audit = 'New' then cn.excludedlongtermcareworker ELSE dc.excludedlongtermcareworker END AS excludedlongtermcareworker
    ,case WHEN cn.audit = 'New' then cn.paymentdate ELSE dc.paymentdate END AS paymentdate
    ,case WHEN cn.audit = 'New' then cn.credentiallastdateofcontact ELSE dc.credentiallastdateofcontact END AS credentiallastdateofcontact
    ,case WHEN cn.audit = 'New' then cn.preferredlanguage ELSE dc.preferredlanguage END AS preferredlanguage
    ,case WHEN cn.audit = 'New' then cn.credentialstatusdate ELSE dc.credentialstatusdate END AS credentialstatusdate
    ,case WHEN cn.audit = 'New' then cn.nctrainingcompletedate ELSE dc.nctrainingcompletedate END AS nctrainingcompletedate
    ,case WHEN cn.audit = 'New' then cn.examscheduleddate ELSE dc.examscheduleddate END AS examscheduleddate
    ,case WHEN cn.audit = 'New' then cn.examscheduledsitecode ELSE dc.examscheduledsitecode END AS examscheduledsitecode
    ,case WHEN cn.audit = 'New' then cn.examscheduledsitename ELSE dc.examscheduledsitename END AS examscheduledsitename
    ,case WHEN cn.audit = 'New' then cn.examtestertype ELSE dc.examtestertype END AS examtestertype
    ,case WHEN cn.audit = 'New' then cn.examemailaddress ELSE dc.examemailaddress END AS examemailaddress
    ,case WHEN cn.audit = 'New' then cn.examdtrecdschedtestdate ELSE dc.examdtrecdschedtestdate END AS examdtrecdschedtestdate
    ,case WHEN cn.audit = 'New' then cn.phonenum ELSE dc.phonenum END AS phonenum
    ,dc.oldhashidkey as oldhashidkey
    ,cn.newhashidkey as newhashidkey
    ,cn.audit as audit
    ,case WHEN cn.audit = 'New' then cn.recordcreateddate ELSE dc.recordcreateddate END AS recordcreateddate
    ,case WHEN cn.audit = 'New' then cn.recordmodifieddate ELSE dc.recordmodifieddate END AS recordmodifieddate
    ,case WHEN cn.audit = 'New' then cn.filemodifieddate ELSE dc.filemodifieddate END AS filemodifieddate
    ,case WHEN cn.audit = 'New' then cn.filename ELSE dc.filename END AS filename
    from credential_new cn FULL OUTER JOIN credential_delta dc on cn.credentialnumber == dc.credentialnumber
    """)
    
print('resultdf df-Credentials after full outer join')
resultdf.printSchema();
resultdf.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

# Filtering by the credentialnumber with latest recordcreateddate
resultdf = resultdf.withColumn("row_number",row_number().over(Window.partitionBy("credentialnumber").orderBy(col("recordcreateddate").desc_nulls_last()))).where(col("row_number") == 1)


print('resultdf df-Credentials after deduplication')
resultdf.printSchema();
resultdf.where(col("credentialnumber").isin({"HM60653245", "RN00090794","OSPI443620J", "OSPI516281C"})).show(10,truncate=False);

resultdf.filter("personid is NULL").show(100,truncate=True)
# Coverting  spark dataframe to glue dynamic dataframe
rawcredentialdeltacdf = DynamicFrame.fromDF(resultdf, glueContext, "rawcredentialdeltacdf")

# ApplyMapping to match the target table
rawcredentialdeltacdf_applymapping = ApplyMapping.apply(frame = rawcredentialdeltacdf, mappings = [("personid", "long", "personid", "long"), ("taxid", "int", "taxid", "int"), ("providernumber", "long", "providernumber", "int"), ("credentialnumber", "string", "credentialnumber", "string"), ("providernamedshs", "string", "providernamedshs", "string"), ("providernamedoh", "string", "providernamedoh", "string"), ("dateofbirth", "string", "dateofbirth", "string"), ("dateofhire", "string", "dateofhire", "string"), ("limitedenglishproficiencyindicator", "string", "limitedenglishproficiencyindicator", "string"), ("firstissuancedate", "string", "firstissuancedate", "string"), ("lastissuancedate", "string", "lastissuancedate", "string"), ("expirationdate", "string", "expirationdate", "string"), ("credentialtype", "string", "credentialtype", "string"), ("credentialstatus", "string", "credentialstatus", "string"), ("lepprovisionalcredential", "string", "lepprovisionalcredential", "string"), ("lepprovisionalcredentialissuedate", "string", "lepprovisionalcredentialissuedate", "string"), ("lepprovisionalcredentialexpirationdate", "string", "lepprovisionalcredentialexpirationdate", "string"), ("actiontaken", "string", "actiontaken", "string"), ("continuingeducationduedate", "string", "continuingeducationduedate", "string"), ("longtermcareworkertype", "string", "longtermcareworkertype", "string"), ("excludedlongtermcareworker", "string", "excludedlongtermcareworker", "string"), ("paymentdate", "string", "paymentdate", "string"), ("credentiallastdateofcontact", "string", "credentiallastdateofcontact", "string"), ("preferredlanguage", "string", "preferredlanguage", "string"), ("credentialstatusdate", "string", "credentialstatusdate", "string"), ("nctrainingcompletedate", "string", "nctrainingcompletedate", "string"), ("examscheduleddate", "string", "examscheduleddate", "string"), ("examscheduledsitecode", "string", "examscheduledsitecode", "string"), ("examscheduledsitename", "string", "examscheduledsitename", "string"), ("examtestertype", "string", "examtestertype", "string"), ("examemailaddress", "string", "examemailaddress", "string"), ("examdtrecdschedtestdate", "string", "examdtrecdschedtestdate", "string"), ("phonenum", "string", "phonenum", "string"),("oldhashidkey","string","hashidkey","string"),("newhashidkey","string","newhashidkey","string"),("audit","string","audit","string"),("recordmodifieddate","timestamp","recordmodifieddate","timestamp"),("filemodifieddate","timestamp","filemodifieddate","timestamp"),("filename","string","filename","string"),("recordcreateddate","timestamp","recordcreateddate","timestamp")], transformation_ctx = "rawcredentialdeltacdf_applymapping")

rawcredentialdeltacdf_selectfields = SelectFields.apply(frame = rawcredentialdeltacdf_applymapping, paths = ["credentialtype", "paymentdate", "limitedenglishproficiencyindicator", "credentialstatus", "dateofhire", "longtermcareworkertype", "actiontaken", "excludedlongtermcareworker", "taxid", "examscheduledsitename", "providernumber", "examdtrecdschedtestdate", "providernamedoh", "examemailaddress", "providernamedshs", "dateofbirth", "credentiallastdateofcontact", "lastissuancedate", "examtestertype", "examscheduleddate", "phonenum", "credentialnumber", "expirationdate", "lepprovisionalcredential", "continuingeducationduedate", "personid", "examscheduledsitecode", "lepprovisionalcredentialexpirationdate", "lepprovisionalcredentialissuedate", "preferredlanguage", "firstissuancedate", "credentialstatusdate", "nctrainingcompletedate","newhashidkey","hashidkey","audit","recordmodifieddate","filename","filemodifieddate","recordcreateddate"], transformation_ctx = "rawcredentialdeltacdf_selectfields")

rawcredentialdeltacdf_matchcatalog_rc = ResolveChoice.apply(frame = rawcredentialdeltacdf_selectfields, choice = "MATCH_CATALOG", database = catalog_database , table_name = catalog_table_prefix+"_raw_credential_delta", transformation_ctx = "rawcredentialdeltacdf_matchcatalog_rc")

rawcredentialdeltacdf_makecol_rc = ResolveChoice.apply(frame = rawcredentialdeltacdf_matchcatalog_rc, choice = "make_cols", transformation_ctx = "rawcredentialdeltacdf_makecol_rc")

# Coverting glue dynamic dataframe to spark dataframe
rawcredentialdelta_final_df = rawcredentialdeltacdf_makecol_rc.toDF()

# Truncating and loading the processed data
mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_NAME
properties = {"user": B2B_USER,"password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
rawcredentialdelta_final_df.write.option("truncate",True).jdbc(url=url, table="raw.credential_delta", mode=mode, properties=properties)

print("Insert an entry into the log table")
max_filedate = datetime.now()
logs_data = [[max_filedate, "glue-credentials-delta-processing", "1"]]
logs_columns = ['lastprocesseddate', 'processname','success']
logs_dataframe = spark.createDataFrame(logs_data, logs_columns)
mode = 'append'
logs_dataframe.write.jdbc(url= url, table= "logs.lastprocessed", mode= mode, properties= properties)


job.commit()