import sys
from awsglue.transforms import SelectFields, ApplyMapping, ResolveChoice, DropNullFields
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import (
    concat,
    col,
    lit,
    substring,
    when,
    length,
    regexp_replace,
    lpad,
)
from pyspark.sql.functions import (
    date_format,
    to_date,
    year,
    date_sub,
    current_date,
    to_timestamp,
    trim,
)
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.types import StringType
from datetime import datetime
import os


args_account = getResolvedOptions(sys.argv, ["environment_type"])
environment_type = args_account["environment_type"]

if environment_type == "dev":
    catalog_database = "postgresrds"
    catalog_table_prefix = "b2bdevdb"
else:
    catalog_database = "seiubg-rds-b2bds"
    catalog_table_prefix = "b2bds"

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Create the Glue Catalog Temp Table for Provider Info , Languages and LastProcessed Tables
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_raw_cdwa"
).toDF().createOrReplaceTempView("cdwaproviders")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_raw_languages"
).toDF().createOrReplaceTempView("languages")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_logs_lastprocessed"
).toDF().createOrReplaceTempView("lastprocessed")

# Below tables were added as place holders for mapping these feilds to staging tables
glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_raw_gender"
).toDF().createOrReplaceTempView("gender")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_raw_ethnicity"
).toDF().createOrReplaceTempView("ethnicity")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_raw_maritalstatus"
).toDF().createOrReplaceTempView("maritalstatus")

glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database, table_name=f"{catalog_table_prefix}_raw_race"
).toDF().createOrReplaceTempView("race")

rawcdwaproviderinfodf = spark.sql(
    """
            select ps.employee_id, ps.personid, ps.first_name,
                    ps.middle_name, ps.last_name,
                    ps.ssn, ps.dob,
                    ps.phone_1, ps.phone_2,
                    ps.email, 
                    ps.mailing_add_1, ps.mailing_add_2, ps.mailing_city, ps.mailing_state, ps.mailing_zip, 
                    ps.physical_add_1, ps.physical_add_2, ps.physical_city, ps.physical_state, ps.physical_zip,
                    case
                         when ps.employee_classification is not null and 
                              ps.employee_classification = 'Adult Child Provider' then 'Adult Child'
                         when ps.employee_classification is not null and 
                              ps.employee_classification = 'Parent Provider' then null
                         when ps.employee_classification is not null and 
                              ps.employee_classification = 'Respite Provider' then 'Respite'
                         when ps.employee_classification is not null and 
                              ps.employee_classification = 'DD Parent Provider' then 'Parent Provider DDD'
                         when (ps.employee_classification is null or ps.employee_classification = '' or
                               ps.employee_classification = 'Orientation & Safety') and 
                               ps.hire_date is not null then 'Orientation & Safety'
                         else ps.employee_classification
                    end as employee_classification, 
                    ps.exempt_status,
                    ps.background_check_date,
                    ps.ie_date,
                    ps.hire_date,
                    ps.classification_start_date,
                    ps.carina_eligible,
                    ps.ahcas_eligible,
                    ps.os_completed,
                    e.value as ethnicity,
                    ps.filemodifieddate, 
                    t.value as preferred_language,
                    m.value as marital_status,
                    g.value as gender,
                    r.value as race,
                    case
                        when ps.employee_classification is not null
                        and ps.employee_classification = 'Standard HCA' then 'SHCA'
                        when ps.employee_classification is not null
                        and ps.employee_classification = 'Adult Child Provider' then 'ADCH'
                        when ps.employee_classification is not null
                        and ps.employee_classification = 'Limited Service Provider' then 'LSPR'
                        when ps.employee_classification is not null
                        and ps.employee_classification = 'Family Provider' then 'FAPR'
                        when ps.employee_classification is not null
                        and ps.employee_classification = 'Respite Provider' then 'RESP'
                        when ps.employee_classification is not null
                        and ps.employee_classification = 'DD Parent Provider' then 'DDPP'
                        when (ps.employee_classification is null
                        or ps.employee_classification = ''
                        or ps.employee_classification = 'Orientation & Safety')
                        and ps.hire_date is not null then 'OSAF'
                        else null
                    end as categorycode
                from
                    cdwaproviders ps
                left join languages t on
                    upper(ps.language) = upper(t.code)
                left join gender g on 
                    upper (ps.gender) = upper(g.code)
                left join ethnicity e on
                    upper(ps.ethnicity)  = upper(e.code) 
                left join maritalstatus m on
                    upper(ps.marital_status)  = upper(m.code)
                left join race r on 
                    upper(ps.race)  = upper(r.code)
                where
                    isvalid = true
                    and recordmodifieddate > (
                    select
                        case
                            when MAX(lastprocesseddate) is null then (current_date-1)
                            else MAX(lastprocesseddate)
                        end as MAXPROCESSDATE
                    from
                        lastprocessed l
                    where
                        processname = 'glue-cdwa-raw-to-staging-person-history'
                        and success = '1'
                        
                        )
                   """
)

# Preparing Physcial and Mailing Address and mailingcountry
rawcdwaproviderinfodf = (
    rawcdwaproviderinfodf.withColumn(
        "physicaladdress",
        concat(
            col("physical_add_1"),
            lit(", "),
            col("physical_city"),
            lit(", "),
            col("physical_state"),
            lit(", "),
            col("physical_zip"),
        ),
    )
    .withColumn(
        "mailingaddress",
        concat(
            col("mailing_add_1"),
            lit(", "),
            col("mailing_city"),
            lit(", "),
            col("mailing_state"),
            lit(", "),
            col("mailing_zip"),
        ),
    )
    .withColumn("mailingcountry", lit("USA"))
)

# Adding Zero's for if has less than 4 digits for Last 4 Of SSN
rawcdwaproviderinfodf = rawcdwaproviderinfodf.withColumn(
    "last_4_ssn",
    when(length(col("ssn")) < 4, lpad(col("ssn"), 4, "0")).otherwise(col("ssn")),
)

# Preparing mobilephone and homephone
rawcdwaproviderinfodf = (
    rawcdwaproviderinfodf.withColumn(
        "phone_1", substring(regexp_replace(col("phone_1"), "[^0-9]", ""), -10, 10)
    )
    .withColumn(
        "mobilephone",
        when(length(col("phone_1")) == 10, concat(lit(1), col("phone_1"))).otherwise(
            None
        ),
    )
    .withColumn(
        "phone_2", substring(regexp_replace(col("phone_2"), "[^0-9]", ""), -10, 10)
    )
    .withColumn(
        "homephone",
        when(length(col("phone_2")) == 10, concat(lit(1), col("phone_2"))).otherwise(
            None
        ),
    )
)

# Validating if Eligible for Advanced Training and exempt by employment
rawcdwaproviderinfodf = rawcdwaproviderinfodf.withColumn(
    "isahcas_eligible",
    when(col("ahcas_eligible") == 1, lit("true")).otherwise(lit("false")),
).withColumn(
    "exempt", when(col("exempt_status") == "Yes", lit("true")).otherwise(lit("false"))
)


# Validation for Date of Birth
rawcdwaproviderinfodf = (
    rawcdwaproviderinfodf.withColumn("dateofbirth", col("dob").cast("string"))
    .withColumn("dateofbirth", to_date(col("dateofbirth"), "yyyyMMdd"))
    .filter(year(col("dateofbirth")) >= lit(1900))
    .filter(col("dateofbirth") <= lit(date_sub(current_date(), ((18 * 365) + 4))))
    .withColumn("dateofbirth", date_format(col("dateofbirth"), "yyyy-MM-dd"))
)

rawcdwaproviderinfodf = (
    rawcdwaproviderinfodf.withColumn("sourcekey", concat(lit("CDWA-"), col("personid")))
    .withColumn(
        "trackingdate",
        to_timestamp(col("classification_start_date").cast("string"), "yyyyMMdd"),
    )
    .withColumn("hiredate", to_timestamp(col("hire_date").cast("string"), "yyyyMMdd"))
    .withColumn(
        "background_check_date",
        to_date(col("background_check_date").cast("string"), "yyyyMMdd"),
    )
    .withColumn("ie_date", to_date(col("ie_date").cast("string"), "yyyyMMdd"))
)

# To remove the leading and traling spaces for string data type columns
df_schema = rawcdwaproviderinfodf.schema
string_columns = []
for column in df_schema:
    if column.dataType == StringType():
        string_columns.append(column.name)
for column in string_columns:
    rawcdwaproviderinfodf = rawcdwaproviderinfodf.withColumn(column, trim(col(column)))


################################ Validation-ends#############################################

rawcdwaproviderinfodfnewdatasource = DynamicFrame.fromDF(
    rawcdwaproviderinfodf, glueContext, "rawcdwaproviderinfodfnewdatasource"
)

cdwaproviderinfoapplymapping = ApplyMapping.apply(
    frame=rawcdwaproviderinfodfnewdatasource,
    mappings=[
        ("preferred_language", "string", "preferred_language", "string"),
        ("language", "string", "language", "string"),
        ("isahcas_eligible", "string", "ahcas_eligible", "boolean"),
        ("background_check_date", "date", "last_background_check_date", "date"),
        ("ie_date", "date", "ie_date", "date"),
        ("physicaladdress", "string", "physicaladdress", "string"),
        ("filemodifieddate", "date", "filemodifieddate", "date"),
        ("mailingaddress", "string", "mailingaddress", "string"),
        ("last_4_ssn", "string", "ssn", "string"),
        ("first_name", "string", "firstname", "string"),
        ("middle_name", "string", "middlename", "string"),
        ("trackingdate", "timestamp", "trackingdate", "timestamp"),
        ("email", "string", "email1", "string"),
        ("mobilephone", "string", "mobilephone", "string"),
        ("homephone", "string", "homephone", "string"),
        ("last_name", "string", "lastname", "string"),
        ("carina_eligible", "string", "iscarinaeligible", "boolean"),
        ("hiredate", "timestamp", "hiredate", "timestamp"),
        ("personid", "string", "cdwa_id", "bigint"),
        ("employee_classification", "string", "workercategory", "string"),
        ("exempt", "string", "exempt", "string"),
        ("dateofbirth", "string", "dob", "string"),
        ("mailing_add_1", "string", "mailingstreet1", "string"),
        ("mailingcountry", "string", "mailingcountry", "string"),
        ("mailing_add_2", "string", "mailingstreet2", "string"),
        ("mailing_city", "string", "mailingcity", "string"),
        ("mailing_state", "string", "mailingstate", "string"),
        ("mailing_zip", "string", "mailingzip", "string"),
        ("sourcekey", "string", "sourcekey", "string"),
        ("employee_id", "decimal(9,0)", "dshsid", "decimal(9,0)"),
        ("categorycode", "string", "categorycode", "string"),
    ],
)

stagingpersonhistoryselectfields = SelectFields.apply(
    frame=cdwaproviderinfoapplymapping,
    paths=[
        "sourcekey",
        "firstname",
        "last_background_check_date",
        "cdwa_id",
        "preferred_language",
        "ahcas_eligible",
        "type",
        "workercategory",
        "credentialnumber",
        "mailingaddress",
        "hiredate",
        "lastname",
        "ssn",
        "tccode",
        "physicaladdress",
        "mobilephone",
        "homephone",
        "modified",
        "personid",
        "exempt",
        "email1",
        "status",
        "ie_date",
        "dob",
        "mailingstreet1",
        "mailingstreet2",
        "mailingcity",
        "mailingstate",
        "mailingzip",
        "dshsid",
        "iscarinaeligible",
        "middlename",
        "mailingcountry",
        "trackingdate",
        "filemodifieddate",
        "categorycode",
    ],
)

stagingpersonhistorymapping = ResolveChoice.apply(
    frame=stagingpersonhistoryselectfields,
    choice="MATCH_CATALOG",
    database=catalog_database,
    table_name=f"{catalog_table_prefix}_staging_personhistory",
)

cdwaproviderinfodropnulls = DropNullFields.apply(frame=stagingpersonhistorymapping)

glueContext.write_dynamic_frame.from_catalog(
    frame=cdwaproviderinfodropnulls,
    database=catalog_database,
    table_name=f"{catalog_table_prefix}_staging_personhistory",
)


# WRITE a record with process/execution time to logs.lastprocessed table
lastprocessed_df = spark.createDataFrame(
    [("glue-cdwa-raw-to-staging-person-history", datetime.now(), "1")],
    schema=["processname", "lastprocesseddate", "success"],
)

# Create Dynamic Frame to log lastprocessed table
lastprocessed_cdf = DynamicFrame.fromDF(
    lastprocessed_df, glueContext, "lastprocessed_cdf"
)

lastprocessed_cdf_applymapping = ApplyMapping.apply(
    frame=lastprocessed_cdf,
    mappings=[
        ("processname", "string", "processname", "string"),
        ("lastprocesseddate", "timestamp", "lastprocesseddate", "timestamp"),
        ("success", "string", "success", "string"),
    ],
)

# Write to postgresql logs.lastprocessed table of the success
glueContext.write_dynamic_frame.from_catalog(
    frame=lastprocessed_cdf_applymapping,
    database=catalog_database,
    table_name=f"{catalog_table_prefix}_logs_lastprocessed",
)

job.commit()
