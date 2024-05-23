import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import concat, col, lit, coalesce, year, current_date, date_format, to_date, date_sub,regexp_replace
from pyspark.sql.functions import to_timestamp
from pyspark.sql.functions import when
from pyspark.sql.functions import *
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import concat,col,sha2,concat_ws,when,md5,current_timestamp
import pyspark.sql.functions as F
from pyspark.sql.functions import substring
import datetime
import pandas
import sys
import json
import re
import csv
import boto3
from datetime import datetime

try:

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
        SecretId=f'{environment_type}/b2bds/s3'
    )
    s3_secrets = json.loads(s3response['SecretString'])
    S3_BUCKET = s3_secrets['datafeeds']
    
    args = getResolvedOptions(sys.argv, ['JOB_NAME'])

    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)
    spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

    datasource0 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_cg_qual_agency_person", transformation_ctx = "datasource0")

    rawdf = datasource0.toDF()
    #filter condition for delta
    rawdf = rawdf.filter("isdelta == 'true' ")
    common_cols=rawdf.columns

    rawdf = rawdf.withColumn("ssn", when(rawdf.cg_status == "1",rawdf.newhire_person_ssn) \
                                    .when(rawdf.cg_status == "2",rawdf.terminated_person_ssn)\
                                    .when(rawdf.cg_status.isNull() ,""))\
                                    .withColumn("dob", when(rawdf.cg_status == "1",rawdf.newhire_person_dob) 
                                    .when(rawdf.cg_status == "2",rawdf.terminated_person_dob)\
                                    .when(rawdf.cg_status.isNull() ,""))\
                                    .withColumn("firstname", when(rawdf.cg_status == "1",rawdf.newhire_person_firstname)
                                    .when(rawdf.cg_status == "2",rawdf.terminated_person_firstname))\
                                    .withColumn("homephone", when(rawdf.cg_status== "1", rawdf.newhire_person_phone2).when(rawdf.cg_status=="2",rawdf.terminated_person_phone))\
                                    .withColumn("mobilephone", when(rawdf.cg_status== "1",rawdf.newhire_person_phone1).when(rawdf.cg_status=="2", rawdf.terminated_person_phone))\
                                    .withColumn("email1",when(rawdf.cg_status=="1",rawdf.newhire_person_email1).when(rawdf.cg_status=="2",rawdf.terminated_person_email))
    rawdf = rawdf.withColumn("dob", coalesce(*[to_date("dob", f) for f in ("MM/dd/yy","MM/dd/yyyy","MM-dd-yyyy","MMddyyyy")])).withColumn("person_dob",when((year(col("dob"))>1900) & (month(col("dob")) < 13) & (dayofmonth(col("dob")) < 32),col("dob")))
    #rawdf= rawdf.withColumn("dob",  col("dob").cast('string'))

    rawdf = rawdf.withColumn("new_dob",rawdf.person_dob)
    rawdf = rawdf.withColumn("new_dob",to_date(col("new_dob"),"yyyy-MM-dd"))
    rawdf=rawdf.filter((F.year(col("new_dob")) >= F.lit(1900)) | (col("cg_status")=="2")).filter((col("new_dob")<=F.lit(F.date_sub(F.current_date(),((18*365)+4)))) | (col("cg_status")=="2")).withColumn("new_dob",date_format(col("new_dob"),"yyyy-MM-dd"))

    # Hash of SSN and DOB
    rawdf = rawdf.withColumn('prefix_ssn', F.when(F.length(rawdf['ssn']) < 4 ,F.lpad(rawdf['ssn'],4,'0')).when(rawdf.ssn == '0', None).otherwise(rawdf['ssn']))
    rawdf_hash = rawdf.withColumn("MD5",md5(concat_ws("",col("prefix_ssn"),col("dob"))))

    #filtering records with invalid demographics
    regex = """^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"""
    phonexpr = """^(?:\+?(\d{1})?-?\(?(\d{3})\)?[\s-\.]?)?(\d{3})[\s-\.]?(\d{4})[\s-\.]?"""

    rawdf_Valid = rawdf_hash.withColumn("is_validphone", when( col("homephone").isNull() | col("homephone").rlike(phonexpr), lit("valid")).otherwise(lit("invalid")))
    rawdf_Valid = rawdf_Valid.withColumn("is_validphone", when( col("mobilephone").isNull() | col("mobilephone").rlike(phonexpr), lit("valid")).otherwise(lit("invalid")))
    rawdf_Valid = rawdf_Valid.withColumn("is_valid_email", when( col("email1").isNull() | col("email1").rlike(regex) | col("email1").rlike("") , lit("valid")).otherwise(lit("invalid")))

    rawdf_Valid=rawdf_Valid.withColumn("mobilephone", when((col("is_validphone")=="invalid"), lit("")).otherwise(col("mobilephone")))
    rawdf_Valid=rawdf_Valid.withColumn("homephone", when((col("is_validphone")=="invalid"), lit("")).otherwise(col("homephone")))

    #even though email in invalid, we should still process the terminated records into employment relationship table
    rawdf_Valid = rawdf_Valid.where(((rawdf_Valid.is_valid_email == "valid") & (rawdf_Valid.cg_status == "1")) | (rawdf_Valid.cg_status =="2") ) 

    #rawdf000 =rawdf_hash.withColumn("hire_date", coalesce(*[to_date("person_hire_date", f) for f in ("MM/dd/yy","MM/dd/yyyy","MM-dd-yyyy", "yyyy-MM-dd","MMddyyyy")]))
    rawdf000 =rawdf_Valid.withColumn("hire_date", coalesce(*[to_date("person_hire_date", f) for f in ("MM/dd/yy","MM/dd/yyyy","MM-dd-yyyy","MMddyyyy")])).withColumn("person_hire_dt",when((year(col("hire_date"))>1900) & (month(col("hire_date")) < 13) & (dayofmonth(col("hire_date")) < 32),col("hire_date")))

    #Fetching records with Invalid hire date #487
    #invalid_df=rawdf000.filter(col("person_hire_dt").isNull() | (col("person_hire_dt") >= current_date())).select(common_cols)
    #invalid_df=invalid_df.dropDuplicates().withColumn("error_reason",lit("Invalid AuthStart date/Hire date"))

    #added filter for checking hire_date should less than current date 
    rawdf000 =rawdf000.filter(((col("hire_date") < current_date()) & (col("cg_status")=="1") )| (col("cg_status") == "2"))
    #rawdf000 =rawdf000.filter(col("hire_date") < current_date())

    #rawdf000= rawdf000.withColumn("person_hire_dt",when((year(col("hire_date"))>1900) & (month(col("hire_date")) < 13) & (dayofmonth(col("hire_date")) < 32),col("hire_date")))
    rawdf000= rawdf000.withColumn("termdate", coalesce(*[to_date("person_termination_date", f) for f in ("yyyy/MM/dd","MM/dd/yy","MM/dd/yyyy","MM-dd-yyyy", "yyyy-MM-dd")]))

    rawdf000= rawdf000.withColumn("termdate",when((year(col("termdate"))>1900) & (month(col("termdate")) < 13) & (dayofmonth(col("termdate")) < 32),col("termdate")))

    rawdf000.createOrReplaceTempView("cg_qual_agency_person")
    rawdf000 = spark.sql("select * from cg_qual_agency_person where (cg_status='1' and person_hire_dt is not null) or (cg_status='2' and terminated_person_id is not null and terminated_person_id<>'' and cast(terminated_person_id as bigint)<>0 and termdate is not null)")

    rawdf00 =rawdf000.withColumn("createdby",(lit("cg_employmentrelationship_gluejob")))
    rawdf01 =rawdf00.withColumn("categorycode",lit("SHCA"))
    rawdf_filtered =rawdf01.withColumn("person_workercategory", lit("Standard HCA"))
    rawdf_filtered01 =rawdf_filtered.withColumn("employername",when(rawdf.employername == "1","102")
                            .when(rawdf_filtered.employername == "2","113")
                            .when(rawdf_filtered.employername == "3","105")
                            .when(rawdf_filtered.employername == "4","106")
                            .when(rawdf_filtered.employername == "5","116")
                            .when(rawdf_filtered.employername == "6","107")
                            .when(rawdf_filtered.employername == "7","117")
                            .when(rawdf_filtered.employername == "8","109")
                            #.when(rawdf_filtered.employername == "9","103")
                            .when(rawdf_filtered.employername == "10","104")
                            .when(rawdf_filtered.employername == "11","111")
                            .when(rawdf_filtered.employername == "12","108")
                            .when(rawdf_filtered.employername == "13","119")
                            .when(rawdf_filtered.employername == "14","120")
                            .when(rawdf_filtered.employername == "15","121"))
                            #.when(rawdf_filtered.employername == "16","426"))

    rawdf_filtered02 =rawdf_filtered01.withColumn("cg_status",when(rawdf_filtered01.cg_status == "1", "Active")
                            .when(rawdf_filtered01.cg_status == "2", "Terminated")
                            .when(rawdf_filtered01.cg_status.isNull() ,""))

    rawdf_filtered03 =rawdf_filtered02.withColumn("branchid",when(rawdf_filtered02.employername == "102", 390)
                            .when(rawdf_filtered02.employername == "113", 398)
                            .when(rawdf_filtered02.employername == "105", 391)
                            .when(rawdf_filtered02.employername == "106", 223)
                            .when(rawdf_filtered02.employername == "116", 201)
                            .when(rawdf_filtered02.employername == "107", 393)
                            .when(rawdf_filtered02.employername == "117", 202)
                            .when(rawdf_filtered02.employername == "109", 394)
                            .when(rawdf_filtered02.employername == "104", 388)
                            .when(rawdf_filtered02.employername == "111", 396)
                            .when(rawdf_filtered02.employername == "108", 246)
                            .when(rawdf_filtered02.employername == "119", 284)
                            .when(rawdf_filtered02.employername == "120", 205)
                            .when(rawdf_filtered02.employername == "121", 206))
                            #.when(rawdf_filtered02.employername == "426", 429))  

    rawdf_filtered04 =rawdf_filtered03.withColumn("sourcekey",when(rawdf_filtered03.branchid == 390, "Addus")
                            .when(rawdf_filtered03.branchid == 398, "AllWaysCaring")
                            .when(rawdf_filtered03.branchid == 391, "Amicable")
                            .when(rawdf_filtered03.branchid == 223 ,"CCS")
                            .when(rawdf_filtered03.branchid == 201, "CDM")
                            .when(rawdf_filtered03.branchid == 393, "Chesterfield")
                            .when(rawdf_filtered03.branchid == 202, "CoastalCap")
                            .when(rawdf_filtered03.branchid == 394, "ConcernedCitizens")
                            .when(rawdf_filtered03.branchid == 388, "FirstChoice")
                            .when(rawdf_filtered03.branchid == 396, "FullLife")
                            .when(rawdf_filtered03.branchid == 246, "KWA")
                            .when(rawdf_filtered03.branchid == 284, "OlyCap")
                            .when(rawdf_filtered03.branchid == 205, "Seamar")
                            .when(rawdf_filtered03.branchid == 206, "SLR"))

    rawdf_filtered05 = rawdf_filtered04.withColumn("priority",(lit("1")))\
                            .withColumn("Role",(lit("CARE")))\
                            .withColumn("isoverridee",(lit("0")))\
                            .withColumn("isignoredd",(lit("0")))

    rawdf_filtered05= rawdf_filtered05.filter(col("employername").isNotNull())

    rawdf_filtered05= rawdf_filtered05.filter(col("branchid").isNotNull())
    invalid_df=rawdf_filtered05.filter((col("firstname").isNull()) | (col("firstname")=='')).select(common_cols).withColumn("error_reason",lit("Invalid firstname"))
    rawdf_filtered05= rawdf_filtered05.filter((col("firstname").isNotNull()) & (col("firstname")!='') )

    rawdf_hash = rawdf_filtered05.withColumn("source",concat(col("sourcekey"),lit("-"), substring(col("MD5"), 1, 10)))
    rawdf_hash= rawdf_hash.withColumn("authstart",col("person_hire_dt")).withColumn("authend",col("termdate"))

    newdatasource0 = DynamicFrame.fromDF(rawdf_hash, glueContext, "newdatasource0")  
    applymapping1 = ApplyMapping.apply(frame = newdatasource0, mappings = [("terminated_person_id", "string", "agencyid", "long"),("person_hire_dt", "date", "hiredate", "timestamp"),("createdby", "string", "createdby", "string"), ("person_workercategory", "string", "workercategory", "string"), ("branchid", "int", "branchid", "int"),("categorycode", "string", "categorycode", "string"), ("cg_status", "string", "empstatus", "string"),("Role", "string", "Role", "string"), ("termdate", "date", "terminationdate", "string"),("source", "string", "source", "string"), ("employername", "string", "employerid", "string"),("priority", "string", "priority", "int"),("homephone", "string", "homephone", "string"),("authstart", "date", "authstart", "string"),("authend", "date", "authend", "string"),("authstart", "date", "trackingdate", "string"),("filemodifieddate", "timestamp", "filedate", "date")], transformation_ctx = "applymapping1")

    selectfields2 = SelectFields.apply(frame = applymapping1, paths = ["branchid", "isoverride", "role", "isignored", "categorycode", "createddate", "filedate", "authend", "modifieddate", "source", "relationshipid", "employeeid", "hiredate", "employerid", "createdby", "authstart", "trackingdate", "modified", "personid", "relationship", "empstatus","Role", "employer_id","agencyid", "terminationdate", "recordcreateddate", "created", "workercategory", "priority", "recordmodifieddate",], transformation_ctx = "selectfields2")

    resolvechoice3 = ResolveChoice.apply(frame = selectfields2, choice = "MATCH_CATALOG", database = catalog_database, table_name = catalog_table_prefix+"_staging_employmentrelationshiphistory", transformation_ctx = "resolvechoice3")

    resolvechoice4 = DropNullFields.apply(frame = resolvechoice3,  transformation_ctx = "resolvechoice4")
    df = resolvechoice4.toDF()

    print("Count of valid records" ,df.count())

    datasink5 = glueContext.write_dynamic_frame.from_catalog(frame = resolvechoice4, database = catalog_database, table_name = catalog_table_prefix+"_staging_employmentrelationshiphistory", transformation_ctx = "datasink5")
    print("count of invalid records while processing to staging employment relationship ", invalid_df.count())
    if invalid_df.count()>0:
        # Group by common columns and aggregate error_reason for Concatenating into a list using collect_list
        grouped_df = invalid_df.groupBy(col("startdate"),col("enddate"),col("status"),col("ipaddress"),col("progress"),col("duration_in_seconds"),col("finished"),col("recordeddate"),col("responseid"),col("recipientlastname"),col("recipientfirstname"),col("recipientemail"),col("externalreference"),col("locationlatitude"),col("locationlongitude"),col("distributionchannel"),col("userlanguage"),col("q_recaptchascore"),col("person_emp_status"),col("agency_firstname"),col("agency_lastname"),col("agency_email"),col("agency_phone"),col("employername"),col("terminated_person_firstname"),col("terminated_person_middlename"),col("terminated_person_lastname"),col("terminated_person_dob"),col("terminated_person_ssn"),col("terminated_person_id"),col("terminated_person_phone"),col("terminated_person_email"),col("terminated_person_street"),col("terminated_person_city"),col("terminated_person_state"),col("terminated_person_zipcode"),col("terminated_person_employerbranch"),col("person_termination_date"),col("newhire_person_firstname"),col("newhire_person_middlename"),col("newhire_person_lastname"),col("newhire_person_dob"),col("newhire_person_ssn"),col("newhire_person_phone1"),col("newhire_person_phone2"),col("newhire_person_phone3"),col("newhire_person_email1"),col("newhire_person_email2"),col("newhire_person_street"),col("newhire_person_city"),col("newhire_person_state"),col("newhire_person_zipcode"),col("preferredlanguage"),col("newhire_personemployerbranch"),col("person_hire_date"),col("exempt"),col("person_workercategory"),col("cg_status"),col("isdelta"),col("filemodifieddate"),col("filename")).agg(concat_ws(", ",F.collect_list("error_reason")).alias("error_reason"))
        
        distinct_invalid_records=grouped_df.select(col("startdate"),col("enddate"),col("status"),col("ipaddress"),col("progress"),col("duration_in_seconds"),col("finished"),col("recordeddate"),col("responseid"),col("recipientlastname"),col("recipientfirstname"),col("recipientemail"),col("externalreference"),col("locationlatitude"),col("locationlongitude"),col("distributionchannel"),col("userlanguage"),col("q_recaptchascore"),col("person_emp_status"),col("agency_firstname"),col("agency_lastname"),col("agency_email"),col("agency_phone"),col("employername"),col("terminated_person_firstname"),col("terminated_person_middlename"),col("terminated_person_lastname"),col("terminated_person_dob"),col("terminated_person_ssn"),col("terminated_person_id"),col("terminated_person_phone"),col("terminated_person_email"),col("terminated_person_street"),col("terminated_person_city"),col("terminated_person_state"),col("terminated_person_zipcode"),col("terminated_person_employerbranch"),col("person_termination_date"),col("newhire_person_firstname"),col("newhire_person_middlename"),col("newhire_person_lastname"),col("newhire_person_dob"),col("newhire_person_ssn"),col("newhire_person_phone1"),col("newhire_person_phone2"),col("newhire_person_phone3"),col("newhire_person_email1"),col("newhire_person_email2"),col("newhire_person_street"),col("newhire_person_city"),col("newhire_person_state"),col("newhire_person_zipcode"),col("preferredlanguage"),col("newhire_personemployerbranch"),col("person_hire_date"),col("exempt"),col("person_workercategory"),col("cg_status"),col("isdelta"),col("filemodifieddate"),col("filename"),col("error_reason"))

        #############################Writing invalid data to logs table######################################################################################
        print("Count of records being written into logs table  ",distinct_invalid_records.count())
        invaliddatasource0 = DynamicFrame.fromDF(distinct_invalid_records, glueContext, "invaliddatasource0")
        mapping_for_logs = ApplyMapping.apply(frame = invaliddatasource0, mappings = [("startdate", "string", "startdate", "string"),("enddate", "string", "enddate", "string"),("status", "string", "status", "string"),("ipaddress", "string", "ipaddress", "string"),("progress", "string", "progress", "string"), ("duration_in_seconds", "string", "duration_in_seconds", "string"), ("finished", "string", "finished", "string"),("recordeddate", "string", "recordeddate", "string"),("responseid", "string", "responseid", "string"), ("recipientlastname", "string", "recipientlastname", "string"), ("recipientfirstname", "string", "recipientfirstname", "string"),("recipientemail", "string", "recipientemail", "string"),("externalreference","string","externalreference","string"),("locationlatitude","string","locationlatitude","string"),("distributionchannel","string","distributionchannel","string"),("userlanguage","string","userlanguage","string"),("q_recaptchascore","string","q_recaptchascore","string"),("person_emp_status","string","person_emp_status","string"),("agency_firstname","string","agency_firstname","string"),("agency_lastname","string","agency_lastname","string"),("agency_email","string","agency_email","string"),("agency_phone","string","agency_phone","string"),("employername","string","employername","string"),("terminated_person_firstname","string","terminated_person_firstname","string"),("terminated_person_middlename","string","terminated_person_middlename","string"),("terminated_person_lastname","string","terminated_person_lastname","string"),("terminated_person_dob","string","terminated_person_dob","string"),("terminated_person_ssn","string","terminated_person_ssn","string"),("terminated_person_id","string","terminated_person_id","string"),("terminated_person_phone","string","terminated_person_phone","string"),("terminated_person_email","string","terminated_person_email","string"),("terminated_person_street","string","terminated_person_street","string"),("terminated_person_city","string","terminated_person_city","string"),("terminated_person_state","string","terminated_person_state","string"),("terminated_person_zipcode","string","terminated_person_zipcode","string"),("terminated_person_employerbranch","string","terminated_person_employerbranch","string"),("person_termination_date","string","person_termination_date","string"),("newhire_person_firstname","string","newhire_person_firstname","string"),("newhire_person_middlename","string","newhire_person_middlename","string"),("newhire_person_lastname","string","newhire_person_lastname","string"),("newhire_person_dob","string","newhire_person_dob","string"),("newhire_person_ssn","string","newhire_person_ssn","string"),("newhire_person_phone1","string","newhire_person_phone1","string"),("newhire_person_phone2","string","newhire_person_phone2","string"),("newhire_person_phone3","string","newhire_person_phone3","string"),("newhire_person_email1","string","newhire_person_email1","string"),("newhire_person_email2","string","newhire_person_email2","string"),("newhire_person_street","string","newhire_person_street","string"),("newhire_person_city","string","newhire_person_city","string"),("newhire_person_state","string","newhire_person_state","string"),("newhire_person_zipcode","string","newhire_person_zipcode","string"),("preferredlanguage","string","preferredlanguage","string"),("newhire_personemployerbranch","string","newhire_personemployerbranch","string"),("person_hire_date","string","person_hire_date","string"),("exempt","string","exempt","string"),("person_workercategory","string","person_workercategory","string"),("cg_status","string","cg_status","string"),("isdelta","string","isdelta","string"),("filemodifieddate", "timestamp", "filemodifieddate", "timestamp"), ("filename","string","filename","string"),("error_reason","string","error_reason","string")], transformation_ctx = "mapping_for_logs")
        
        
        selectfieldslogs = SelectFields.apply(frame = mapping_for_logs, paths = ["startdate","enddate","status","ipaddress","progress","duration_in_seconds","finished","recordeddate","responseid","recipientlastname","recipientfirstname","recipientemail","externalreference","locationlatitude","locationlongitude","distributionchannel","userlanguage","q_recaptchascore","person_emp_status","agency_firstname","agency_lastname","agency_email","agency_phone","employername","terminated_person_firstname","terminated_person_middlename","terminated_person_lastname","terminated_person_dob","terminated_person_ssn","terminated_person_id","terminated_person_phone","terminated_person_email","terminated_person_street","terminated_person_city","terminated_person_state","terminated_person_zipcode","terminated_person_employerbranch","person_termination_date","newhire_person_firstname","newhire_person_middlename","newhire_person_lastname","newhire_person_dob","newhire_person_ssn","newhire_person_phone1","newhire_person_phone2","newhire_person_phone3","newhire_person_email1","newhire_person_email2","newhire_person_street","newhire_person_city","newhire_person_state","newhire_person_zipcode","preferredlanguage","newhire_personemployerbranch","person_hire_date","exempt","person_workercategory","cg_status","isdelta","filemodifieddate","filename","error_reason"], transformation_ctx = "selectfieldslogs")
        
        
        resolvechoicelogs = ResolveChoice.apply(frame = selectfieldslogs, choice = "MATCH_CATALOG", database = catalog_database, table_name = catalog_table_prefix+"_logs_qualtricsagencyerrors", transformation_ctx = "resolvechoicelogs")
        
        resolvechoicelogs2 = DropNullFields.apply(frame = resolvechoicelogs,  transformation_ctx = "resolvechoicelogs2")
        df_logs = resolvechoicelogs2.toDF()
        datasinklogs = glueContext.write_dynamic_frame.from_catalog(frame = resolvechoicelogs2, database = catalog_database, table_name = catalog_table_prefix+"_logs_qualtricsagencyerrors", transformation_ctx = "datasinklogs")
        print("Successfully logged invalid records into logs table")

    ##########################################Extracting invalid records as csv file to S3####################################################################
    error_data_source = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_logs_qualtricsagencyerrors", transformation_ctx = "error_data_source")
    error_data_source = error_data_source.toDF()
    error_data_source.createOrReplaceTempView("qualtrics_logs")
    error_df = spark.sql("Select * from qualtrics_logs where date(recordcreateddate)>= current_date")
    print("All invalid records while processing records from raw to staging person history & employment history tables are ", error_df.count())
    if error_df.count()>0:
        pandas_df = error_df.toPandas()
        print("Exporting error report to S3 bucket")
        # Export the invalid records to a S3 bucket
        filename = error_df.filter(error_df.recordcreateddate >= current_date()).select(max(error_df.filename)).collect()[0][0]
        name_suffix = re.sub(r"\D", "", filename)
        print("filename is ", name_suffix)
        #print(S3_BUCKET)
        pandas_df.to_csv("s3://"+S3_BUCKET+"/Outbound/qualtrics/errorlog/Qualtrics_Agency_Errors_" + name_suffix +".csv", header=True, index=None,quotechar='"',encoding='utf-8', sep=',',quoting=csv.QUOTE_ALL)
        print("Successfully exported the error report to S3 path /Outbound/qualtrics/errorlog/Qualtrics_Agency_Errors ")

    # WRITE a record with process/execution time to logs.lastprocessed table
    lastprocessed_df = spark.createDataFrame(
        [('glue-qualtrics-raw-to-employmentrelationshiphistory', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])
    
    # Create Dynamic Frame to log lastprocessed table
    lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext, "lastprocessed_cdf")
    
    lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[
        ("processname", "string", "processname", "string"),
        ("lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"),
        ("success", "string", "success", "string")])
    
    # Write to PostgreSQL logs.lastprocessed table of the success
    glueContext.write_dynamic_frame.from_catalog(
        frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")


    print('done')

    job.commit()
except Exception as e:
    print("An error occurred:", e)