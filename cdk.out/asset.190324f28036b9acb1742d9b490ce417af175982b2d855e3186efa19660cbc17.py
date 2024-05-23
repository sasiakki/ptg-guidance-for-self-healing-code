import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
import boto3
import json


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

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

mode = "overwrite"
url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_DBNAME
properties = {"user": B2B_USER, "password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}

s3resource = boto3.resource('s3')
s3bucket = s3resource.Bucket(''+S3_BUCKET+'')
#sourcepath = "s3://"+S3_BUCKET+"/Inbound/raw/Learningpath/"  


# Script generated for node PostgreSQL table
glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_prod_transcript",
).toDF().createOrReplaceTempView("prod_transcript")

glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name=catalog_table_prefix+"_prod_trainingrequirement",
).toDF().createOrReplaceTempView("prod_trainingrequirement")

glueContext.create_dynamic_frame.from_catalog(
    database = catalog_database,
    table_name = catalog_table_prefix+"_staging_traininghistory",
).toDF().createOrReplaceTempView("staging_traininghistory")

df = spark.sql("""with transcript_delta as
(select * from prod_transcript where personid in (
select personid from prod_transcript where recordcreateddate > (select max(recordcreateddate) from staging_traininghistory) 
and trainingid is null and learningpath is not null)),
learningpath_temp as 
(select k.learningpath as learningpath_delta,k.personid as person_id,k.trainingprogramcode  as tpcode from (select personid,trainingprogramcode,learningpath,ROW_NUMBER() OVER ( PARTITION BY personid, trainingprogramcode ORDER BY completeddate desc ) completionsrank 
from transcript_delta  ) k where k.completionsrank = 1)
select * from transcript_delta t 
join learningpath_temp l on t.personid = l.person_id and t.trainingprogramcode = l.tpcode""")
df.show()
df.createOrReplaceTempView("completions")

df1 = spark.sql("""select t.transcriptid, t.personid, t.completeddate,t.trainingprogramcode,t.credithours,t.trainingid as transcript_trainingid,status,
tr.requiredhours as tr_requiredhours,tr.earnedhours as tr_earnedhours,tr.transferredhours as tr_transferhours,tr.trainingid as ttrainingid,t.learningpath as transcriptlpath , 
tr.learningpath as traininglpath,t.learningpath_delta,t.trainingid as transc_trainingid
from completions t join prod_trainingrequirement tr
on t.personid = tr.personid and t.trainingprogramcode = tr.trainingprogramcode
where tr.status = 'active' 
and cast(t.completeddate as date) between cast(tr.trackingdate as date) 
and cast(coalesce(tr.duedateextension,tr.duedate) as date)
order by t.completeddate desc""")
df1.show()
df1.createOrReplaceTempView("tr_updates")

learningpaths_df=spark.sql("""with final_df as (
select transcriptid, personid,completeddate,credithours,transc_trainingid,status,traininglpath,learningpath_delta,transcriptlpath,
trainingprogramcode,tr_transferhours,tr_requiredhours,
case 
when traininglpath is null and transcriptlpath <> learningpath_delta    
then null
when traininglpath is  null and transcriptlpath  = learningpath_delta    
then ttrainingid
when traininglpath is not null and transcriptlpath <> learningpath_delta then null
else ttrainingid
end as trainingid
from tr_updates),df_final as(
select transcriptid,personid,credithours,completeddate,tr_transferhours,tr_requiredhours,trainingprogramcode,traininglpath,transcriptlpath,learningpath_delta,trainingid,status,
string((SELECT SUM(credithours) FROM final_df t1 WHERE t1.trainingid = t2.trainingid AND t1.Personid = t2.Personid AND t1.learningpath_delta = t2.learningpath_delta) ) 
as earnedhours
 from final_df t2)
select * , coalesce(tr_transferhours,0.0) + coalesce(earnedhours,0.0) as total_hours,
case 
when coalesce(tr_requiredhours,0) = coalesce(tr_transferhours,0) + coalesce(earnedhours,0) then 'closed'
else 'active'
end as status from df_final""")
learningpaths_df.show()

learningpath_update_datacatalogtable = DynamicFrame.fromDF(learningpaths_df, glueContext, "learningpath_update_datacatalogtable")


# Script generated for node ApplyMapping
learningpath_update = ApplyMapping.apply(
    frame=learningpath_update_datacatalogtable,
    mappings=[
        
        ("transcriptid", "long", "transcriptid", "long"),
        ("trainingid", "string", "trainingid", "string"),
        ("trainingprogramcode", "string", "trainingprogramcode", "string"),
        ("learningpath_delta", "string", "learningpath", "string"),
        ("completeddate", "string", "completeddate", "date"),
        ("personid", "long", "personid", "long"),
        ("earnedhours", "string", "earnedhours", "double"),
        ("status", "string", "status", "string"),

    ],
    transformation_ctx="learningpath_update",
)

temp_learningpath_update = learningpath_update.toDF()
temp_learningpath_update.write.option("truncate",True).jdbc(url=url, table="staging.learningpath_updates", mode=mode, properties=properties)


job.commit()
