import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import lit, coalesce, year, current_date, date_format, to_date, dayofmonth,regexp_replace
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import concat,col,concat_ws,when,md5,substring, trim, month, length, lpad, date_sub, collect_list
from pyspark.sql.types import StringType
from datetime import datetime

## @params: [JOB_NAME]
try:
    args_account = getResolvedOptions(sys.argv, ["environment_type"])
    environment_type = args_account['environment_type']

    if environment_type == 'dev':
        catalog_database = 'postgresrds'
        catalog_table_prefix = 'b2bdevdb'
    else:
        catalog_database = 'seiubg-rds-b2bds'
        catalog_table_prefix = 'b2bds'

    args = getResolvedOptions(sys.argv, ['JOB_NAME'])
    
    sc = SparkContext()
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)
    spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
    
    #datasource0 = glueContext.create_dynamic_frame.from_catalog(database = catalog_database, table_name = catalog_table_prefix+"_raw_cg_qual_agency_person", transformation_ctx = "datasource0")
    
    # glue-qualtrics-raw-to-person-history
    # This Glue Job Moves Agency Caregive Intake info data data from  raw.cg_qual_agency_person staging personhistory table
    # Reading the glue catalog table for the raw.cg_qual_agency_person for  Caregive Intake info data
    glueContext.create_dynamic_frame.from_catalog(
        database = catalog_database, 
        table_name = f"{catalog_table_prefix}_raw_cg_qual_agency_person",)\
        .toDF().createOrReplaceTempView("cg_qual_agency_person")
    
    glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")\
    .toDF().createOrReplaceTempView("lastprocessed")
    
    rawdf = spark.sql("""
            select ps.* from cg_qual_agency_person ps
                where
                    ps.recordmodifieddate > (
                    select
                        case
                            when MAX(lastprocesseddate) is null then (current_date-1)
                            else MAX(lastprocesseddate)
                        end as MAXPROCESSDATE
                    from
                        lastprocessed l
                    where
                        processname = 'glue-qualtrics-raw-to-person-history'
                        and success = '1'
                        )
                   """)
    
    #filter condition for delta 
    rawdf = rawdf.filter("isdelta == 'true'")
    common_cols=rawdf.columns
    print("############################Job execution started################################")
    print("Count of available delta records ", rawdf.count())
    rawdf.createOrReplaceTempView("cg_qual_agency_person")
    
    rawdf =rawdf.withColumn("newaddress",concat(col("newhire_person_street"),lit(", "), col("newhire_person_city"),lit(", "), col("newhire_person_state"),lit(", "), col("newhire_person_zipcode"))).withColumn("terminatedaddress",concat(col("terminated_person_street"),lit(", "), col("terminated_person_city"),lit(", "), col("terminated_person_state"),lit(", "), col("terminated_person_zipcode"))).withColumn("mailingcountry",lit("USA"))
    rawdf = rawdf.withColumn("exempt", when(col("exempt") =="1","true").otherwise("false")).withColumn("status", when(col("cg_status")=="1","Active")
              .when(col("cg_status")=="2","Terminated"))
    
    rawdf =rawdf.withColumn("hire_date", coalesce(*[to_date("person_hire_date", f) for f in ("MM/dd/yy","MM/dd/yyyy","MM-dd-yyyy","MMddyyyy")])).withColumn("person_hire_dt",when((year(col("hire_date"))>1900) & (month(col("hire_date")) < 13) & (dayofmonth(col("hire_date")) < 32),col("hire_date")))
    
    #Fetching records with Invalid hire date #487
    invalid_df=rawdf.filter((col("cg_status")=="1") & (col("person_hire_dt").isNull() | (col("person_hire_dt") >= current_date()))).select(common_cols)
    invalid_df=invalid_df.dropDuplicates().withColumn("error_reason",lit("Invalid hire date"))
    
    rawdf = rawdf.filter(((col("hire_date") < current_date()) & (col("cg_status")=="1") )| (col("cg_status") == "2"))
    
    
    rawdf_filtered = rawdf.withColumn("firstname", when(rawdf.cg_status == "1",rawdf.newhire_person_firstname) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_firstname) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("lastname", when(rawdf.cg_status == "1",rawdf.newhire_person_lastname) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_lastname) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("middlename", when(rawdf.cg_status == "1",rawdf.newhire_person_middlename) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_middlename) 
                                     .when(rawdf.cg_status.isNull() ,"")) .withColumn("email1", when(rawdf.cg_status == "1",rawdf.newhire_person_email1) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_email) 
                                     .when(rawdf.cg_status.isNull() ,""))  .withColumn("homephone", when(rawdf.cg_status == "1",rawdf.newhire_person_phone2) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_phone)
                                     .when(rawdf.cg_status.isNull() ,""))  .withColumn("mobilephone", when(rawdf.cg_status == "1",rawdf.newhire_person_phone1) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_phone)                                  
                                     .when(rawdf.cg_status.isNull() ,"")) .withColumn("mailingaddress", when(rawdf.cg_status == "1",rawdf.newaddress) 
                                     .when(rawdf.cg_status == "2",rawdf.terminatedaddress) 
                                     .when(rawdf.cg_status.isNull() ,""))  .withColumn("ssn", when(rawdf.cg_status == "1",rawdf.newhire_person_ssn) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_ssn) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("dob", when(rawdf.cg_status == "1",rawdf.newhire_person_dob) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_dob) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("mailingstreet1", when(rawdf.cg_status == "1",rawdf.newhire_person_street) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_street) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("mailingcity", when(rawdf.cg_status == "1",rawdf.newhire_person_city) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_city) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("mailingstate", when(rawdf.cg_status == "1",rawdf.newhire_person_state) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_state) 
                                     .when(rawdf.cg_status.isNull() ,"")).withColumn("mailingzip", when(rawdf.cg_status == "1",rawdf.newhire_person_zipcode) 
                                     .when(rawdf.cg_status == "2",rawdf.terminated_person_zipcode) 
                                     .when(rawdf.cg_status.isNull() ,""))
                                     
    
    
    rawdf_filtered = rawdf_filtered.withColumn("dob", coalesce(*[to_date("dob", f) for f in ("MM/dd/yy","MM/dd/yyyy","MM-dd-yyyy","MMddyyyy")])).withColumn("person_dob",when((year(col("dob"))>1900) & (month(col("dob")) < 13) & (dayofmonth(col("dob")) < 32),col("dob")))
    
    #Fetching records with Invalid DOB - part 1 #487
    invalid_df = invalid_df.union(rawdf_filtered.filter(col("person_dob").isNull()).select(common_cols).withColumn("error_reason",lit("Invalid DOB")))
    
    
    rawdf_filtered = rawdf_filtered.withColumn('prefix_ssn', when(length(rawdf_filtered['ssn']) < 4 ,lpad(rawdf_filtered['ssn'],4,'0')).when(rawdf_filtered.ssn == '0', None).otherwise(rawdf_filtered['ssn']))
    rawdf_filtered= rawdf_filtered.withColumn("person_dob",  col("person_dob").cast('string'))
    
    #Fetching invalid ssn records - #487
    invalid_df= invalid_df.union(rawdf_filtered.filter(col("prefix_ssn").isNull()).select(common_cols).withColumn("error_reason",lit("Invalid SSN")))
    
    
    rawdf_filtered = rawdf_filtered.withColumn("MD5",md5(concat_ws("",col("prefix_ssn"),col("person_dob"))))
    rawdf_filtered.createOrReplaceTempView("cg_qual_agency_person")
    
    #Fetching invalid termintaed records #487
    term_df=spark.sql("Select * from cg_qual_agency_person where status='Terminated' and (terminated_person_id is null or person_termination_date is null or cast(terminated_person_id as bigint)=0 or person_termination_date='' or terminated_person_id='')")
    invalid_df = invalid_df.union(term_df.select(common_cols).withColumn("error_reason", lit("Invalid Person ID or Termination Date")))
    
    #Fetching invalid new hires #487
    invalid_df=invalid_df.union(rawdf_filtered.filter((col("status")=="Active") & col("hire_date").isNull()).select(common_cols).withColumn("error_reason",lit("Hire Date is null for active user")))
    
    rawdf_filtered = spark.sql("select * from cg_qual_agency_person where (status='Active' and hire_date is not null) or (status='Terminated' and terminated_person_id is not null and person_termination_date is not null and terminated_person_id<>'' and person_termination_date<>'')")
    
    rawdf_filtered01 =rawdf_filtered.withColumn("categorycode",lit("SHCA"))\
                  .withColumn("employername",when(rawdf.employername == "1","102")
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
    rawdf_filtered02= rawdf_filtered01.withColumn("branchid",when(rawdf_filtered01.employername == "102", 390)
                            .when(rawdf_filtered01.employername == "113", 398)
                            .when(rawdf_filtered01.employername == "105", 391)
                            .when(rawdf_filtered01.employername == "106", 223)
                            .when(rawdf_filtered01.employername == "116", 201)
                            .when(rawdf_filtered01.employername == "107", 393)
                            .when(rawdf_filtered01.employername == "117", 202)
                            .when(rawdf_filtered01.employername == "109", 394)
                            .when(rawdf_filtered01.employername == "104", 388)
                            .when(rawdf_filtered01.employername == "111", 396)
                            .when(rawdf_filtered01.employername == "108", 246)
                            .when(rawdf_filtered01.employername == "119", 284)
                            .when(rawdf_filtered01.employername == "120", 205)
                            .when(rawdf_filtered01.employername == "121", 206))
                            #.when(rawdf_filtered01.employername == "426", 429))
    
    rawdf_filtered03 =rawdf_filtered02.withColumn("source",when(rawdf_filtered02.branchid == 390, "Addus")
                            .when(rawdf_filtered02.branchid == 398, "AllWaysCaring")
                            .when(rawdf_filtered02.branchid == 391, "Amicable")
                            .when(rawdf_filtered02.branchid == 223 ,"CCS")
                            .when(rawdf_filtered02.branchid == 201, "CDM")
                            .when(rawdf_filtered02.branchid == 393, "Chesterfield")
                            .when(rawdf_filtered02.branchid == 202, "CoastalCap")
                            .when(rawdf_filtered02.branchid == 394, "ConcernedCitizens")
                            .when(rawdf_filtered02.branchid == 388, "FirstChoice")
                            .when(rawdf_filtered02.branchid == 396, "FullLife")
                            .when(rawdf_filtered02.branchid == 246, "KWA")
                            .when(rawdf_filtered02.branchid == 284, "OlyCap")
                            .when(rawdf_filtered02.branchid == 205, "Seamar")
                            .when(rawdf_filtered02.branchid == 206, "SLR"))\
                            .withColumn("person_workercategory",lit("Standard HCA"))\
                            .withColumn("termdate",to_date(col("person_termination_date"),"MM-dd-yyyy"))\
                            .withColumn("language", when(rawdf_filtered02.preferredlanguage == "1", "English")
                            .when(rawdf_filtered02.preferredlanguage == "2", "Amharic")
                            .when(rawdf_filtered02.preferredlanguage == "3", "Arabic")
                            .when(rawdf_filtered02.preferredlanguage == "4", "Chinese")
                            .when(rawdf_filtered02.preferredlanguage == "5", "Farsi")
                            .when(rawdf_filtered02.preferredlanguage == "6", "Khmer")
                            .when(rawdf_filtered02.preferredlanguage == "7", "Korean")
                            .when(rawdf_filtered02.preferredlanguage == "8", "Lao")
                            .when(rawdf_filtered02.preferredlanguage == "9", "Nepali")
                            .when(rawdf_filtered02.preferredlanguage == "10", "Punjabi")
                            .when(rawdf_filtered02.preferredlanguage == "11", "Russian")
                            .when(rawdf_filtered02.preferredlanguage == "12", "Samoan")
                            .when(rawdf_filtered02.preferredlanguage == "13", "Somali")
                            .when(rawdf_filtered02.preferredlanguage == "14", "Spanish")
                            .when(rawdf_filtered02.preferredlanguage == "15", "Tagalog")
                            .when(rawdf_filtered02.preferredlanguage == "16", "Ukrainian")
                            .when(rawdf_filtered02.preferredlanguage == "17", "Vietnamese"))\
                            
    # Hash of SSN and DOB
    rawdf_filtered05= rawdf_filtered03.filter(col("employername").isNotNull())
    
    #Fetching records with invalid Branch #487
    invalid_df=invalid_df.union(rawdf_filtered05.filter(col("branchid").isNull()).select(common_cols).withColumn("error_reason",lit("Invalid Branch ID")))
    
    rawdf_filtered05= rawdf_filtered05.filter(col("branchid").isNotNull())
    
    #Fetching records with invalid employername #487
    invalid_df=invalid_df.union(rawdf_filtered03.filter(col("employername").isNull()).select(common_cols).withColumn("error_reason",lit("Invalid Employer Name")))
    
    rawdf_hash = rawdf_filtered05.withColumn("sourcehashkey",concat(col("source"),lit("-"),substring(col("MD5"), 1, 10)))
    
    ################################Validation-starts############################################
    
    
    regex = """^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"""
    phonexpr = """^(?:\+?(\d{1})?-?\(?(\d{3})\)?[\s-\.]?)?(\d{3})[\s-\.]?(\d{4})[\s-\.]?"""
    
    
    
    rawdf_Valid = rawdf_hash.withColumn("is_validphone", when( col("homephone").isNull() | col("homephone").rlike(phonexpr), lit("valid")).otherwise(lit("invalid")))
    rawdf_Valid = rawdf_Valid.withColumn("is_validphone", when( col("mobilephone").isNull() | col("mobilephone").rlike(phonexpr), lit("valid")).otherwise(lit("invalid")))
    rawdf_Valid = rawdf_Valid.withColumn("is_valid_email", when( col("email1").isNull() | col("email1").rlike(regex) | col("email1").rlike("") , lit("valid")).otherwise(lit("invalid")))
    
    rawdf_Valid=rawdf_Valid.withColumn("mobilephone", when((col("is_validphone")=="invalid"), lit("")).otherwise(col("mobilephone")))
    rawdf_Valid=rawdf_Valid.withColumn("homephone", when((col("is_validphone")=="invalid"), lit("")).otherwise(col("homephone")))

    #even though email is invalid, we should still process the terminated records into employment relationship table
     

    
    #Fetching records with invalid demographs #487
    invalid_df=invalid_df.union(rawdf_Valid.filter(col("is_valid_email")=="invalid").select(common_cols).withColumn("error_reason",lit("Invalid Email")))

    rawdf_Valid = rawdf_Valid.where(rawdf_Valid.is_valid_email == "valid")

    #rawdf_Valid.select("newaddress","terminatedaddress","hire_date","firstname", "sourcehashkey","dob","person_workercategory","categorycode").show()
    # Validation for Date of Birth 
    
    rawdf_Valid = rawdf_Valid.withColumn("new_dob",rawdf_Valid.person_dob).withColumn("homephone",concat(lit("1"),regexp_replace(col('homephone'), '[^A-Z0-9_]', ''))).withColumn("mobilephone",concat(lit("1"),regexp_replace(col('mobilephone'), '[^A-Z0-9_]', '')))
    
    #Fetching records with invalid DOB - part 2 #487
    invalid_dob_df2=rawdf_Valid.withColumn("new_dob",to_date(col("new_dob"),"yyyy-MM-dd")).filter(year(col("new_dob")) < lit(1900))
    invalid_dob_df2=invalid_dob_df2.union(rawdf_Valid.filter(col("new_dob")>lit(date_sub(current_date(),((18*365)+4)))).withColumn("new_dob",date_format(col("new_dob"),"yyyy-MM-dd")))
    invalid_df=invalid_df.union(invalid_dob_df2.select(common_cols).withColumn("error_reason",lit("Invalid DOB - under 18")))
    
    rawdf_Valid = rawdf_Valid.withColumn("new_dob",to_date(col("new_dob"),"yyyy-MM-dd")).filter(year(col("new_dob")) >= lit(1900)).filter(col("new_dob")<=lit(date_sub(current_date(),((18*365)+4)))).withColumn("new_dob",date_format(col("new_dob"),"yyyy-MM-dd"))
    
    
    
    
    ################################Validation-ends#############################################
    
    df_schema = rawdf_Valid.schema
    string_columns = []
    for column in df_schema:
        if column.dataType == StringType():
            string_columns.append(column.name)
    for column in string_columns:
        rawdf_Valid = rawdf_Valid.withColumn(column, trim(col(column)))

    newdatasource0 = DynamicFrame.fromDF(rawdf_Valid, glueContext, "newdatasource0")
    applymapping1 = ApplyMapping.apply(frame = newdatasource0, mappings = [("lastname", "string", "lastname", "string"),("middlename", "string", "middlename", "string"),("sourcehashkey", "string", "sourcekey", "string"),("new_dob", "string", "dob", "string"),("terminated_person_id", "string", "agencyid", "long"), ("email1", "string", "email1", "string"),("language", "string", "preferred_language", "string"),("mailingaddress", "string", "mailingaddress", "string"), ("prefix_ssn", "string", "ssn", "string"), ("person_workercategory", "string", "workercategory", "string"),("status", "string", "status", "string"),("filemodifieddate", "timestamp", "filemodifieddate", "date"), ("categorycode", "string", "categorycode", "string"),("firstname", "string", "firstname", "string"), ("person_hire_dt", "date", "hiredate", "timestamp"),("person_hire_dt", "date", "trackingdate", "timestamp"), ("homephone", "string", "homephone", "string"),("mobilephone", "string", "mobilephone", "string"), ("exempt", "string", "exempt", "string"),("mailingstreet1","string","mailingstreet1","string"),("mailingcity","string","mailingcity","string"),("mailingstate","string","mailingstate","string"),("mailingzip","string","mailingzip","string"),("mailingcountry","string","mailingcountry","string")], transformation_ctx = "applymapping1")
    
    
    selectfields2 = SelectFields.apply(frame = applymapping1, paths = ["sourcekey", "firstname", "goldenrecordid", "cdwa_id", "language", "type", "workercategory", "credentialnumber", "mailingaddress", "categorycode", "dob", "hiredate","middlename" ,"lastname","trackingdate","preferred_language", "ssn", "tccode", "physicaladdress", "homephone", "mobilephone","modified", "exempt", "email1","agencyid", "status","filemodifieddate","mailingstreet1","mailingcity","mailingstate","mailingcountry","mailingzip","filedate"], transformation_ctx = "selectfields2")
    
    
    resolvechoice3 = ResolveChoice.apply(frame = selectfields2, choice = "MATCH_CATALOG", database = catalog_database, table_name = catalog_table_prefix+"_staging_personhistory", transformation_ctx = "resolvechoice3")
    
    resolvechoice4 = DropNullFields.apply(frame = resolvechoice3,  transformation_ctx = "resolvechoice4")
    df = resolvechoice4.toDF()
    print(" Count of valid records  " ,df.count())
    
    datasink5 = glueContext.write_dynamic_frame.from_catalog(frame = resolvechoice4, database = catalog_database, table_name = catalog_table_prefix+"_staging_personhistory", transformation_ctx = "datasink5")
    if invalid_df.count()>0:
        # Group by common columns and aggregate error_reason for Concatenating into a list using collect_list
        grouped_df = invalid_df.groupBy(col("startdate"),col("enddate"),col("status"),col("ipaddress"),col("progress"),col("duration_in_seconds"),col("finished"),col("recordeddate"),col("responseid"),col("recipientlastname"),col("recipientfirstname"),col("recipientemail"),col("externalreference"),col("locationlatitude"),col("locationlongitude"),col("distributionchannel"),col("userlanguage"),col("q_recaptchascore"),col("person_emp_status"),col("agency_firstname"),col("agency_lastname"),col("agency_email"),col("agency_phone"),col("employername"),col("terminated_person_firstname"),col("terminated_person_middlename"),col("terminated_person_lastname"),col("terminated_person_dob"),col("terminated_person_ssn"),col("terminated_person_id"),col("terminated_person_phone"),col("terminated_person_email"),col("terminated_person_street"),col("terminated_person_city"),col("terminated_person_state"),col("terminated_person_zipcode"),col("terminated_person_employerbranch"),col("person_termination_date"),col("newhire_person_firstname"),col("newhire_person_middlename"),col("newhire_person_lastname"),col("newhire_person_dob"),col("newhire_person_ssn"),col("newhire_person_phone1"),col("newhire_person_phone2"),col("newhire_person_phone3"),col("newhire_person_email1"),col("newhire_person_email2"),col("newhire_person_street"),col("newhire_person_city"),col("newhire_person_state"),col("newhire_person_zipcode"),col("preferredlanguage"),col("newhire_personemployerbranch"),col("person_hire_date"),col("exempt"),col("person_workercategory"),col("cg_status"),col("isdelta"),col("filemodifieddate"),col("filename")).agg(concat_ws(", ",collect_list("error_reason")).alias("error_reason"))
        
        distinct_invalid_records=grouped_df.select(col("startdate"),col("enddate"),col("status"),col("ipaddress"),col("progress"),col("duration_in_seconds"),col("finished"),col("recordeddate"),col("responseid"),col("recipientlastname"),col("recipientfirstname"),col("recipientemail"),col("externalreference"),col("locationlatitude"),col("locationlongitude"),col("distributionchannel"),col("userlanguage"),col("q_recaptchascore"),col("person_emp_status"),col("agency_firstname"),col("agency_lastname"),col("agency_email"),col("agency_phone"),col("employername"),col("terminated_person_firstname"),col("terminated_person_middlename"),col("terminated_person_lastname"),col("terminated_person_dob"),col("terminated_person_ssn"),col("terminated_person_id"),col("terminated_person_phone"),col("terminated_person_email"),col("terminated_person_street"),col("terminated_person_city"),col("terminated_person_state"),col("terminated_person_zipcode"),col("terminated_person_employerbranch"),col("person_termination_date"),col("newhire_person_firstname"),col("newhire_person_middlename"),col("newhire_person_lastname"),col("newhire_person_dob"),col("newhire_person_ssn"),col("newhire_person_phone1"),col("newhire_person_phone2"),col("newhire_person_phone3"),col("newhire_person_email1"),col("newhire_person_email2"),col("newhire_person_street"),col("newhire_person_city"),col("newhire_person_state"),col("newhire_person_zipcode"),col("preferredlanguage"),col("newhire_personemployerbranch"),col("person_hire_date"),col("exempt"),col("person_workercategory"),col("cg_status"),col("isdelta"),col("filemodifieddate"),col("filename"),col("error_reason"))
        print("Count of invalid records ",distinct_invalid_records.count())
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
       
    # WRITE a record with process/execution time to logs.lastprocessed table
    lastprocessed_df = spark.createDataFrame(
        [('glue-qualtrics-raw-to-person-history', datetime.now(), "1")], schema=["processname", "lastprocesseddate", "success"])

    # Create Dynamic Frame to log lastprocessed table
    lastprocessed_cdf = DynamicFrame.fromDF(lastprocessed_df, glueContext,"lastprocessed_cdf")

    lastprocessed_cdf_applymapping = ApplyMapping.apply(frame=lastprocessed_cdf, mappings=[("processname", "string", "processname", "string"), (
        "lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"), ("success", "string", "success", "string")])

    # Write to postgresql logs.lastprocessed table of the success
    glueContext.write_dynamic_frame.from_catalog(
        frame=lastprocessed_cdf_applymapping, database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed")

    print('##################################Job completed######################################')
    job.commit()
except Exception as e:
    print("An error occurred:", e)
    raise Exception ("Glue Job Failed")
