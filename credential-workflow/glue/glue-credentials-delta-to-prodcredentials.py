# import sys
# from awsglue.transforms import *
# from awsglue.utils import getResolvedOptions
# from pyspark.context import SparkContext
# from awsglue.context import GlueContext
# from awsglue.job import Job
# from pyspark.sql.functions import concat,col,sha2,concat_ws,when,md5,current_timestamp,row_number
# from awsglue.dynamicframe import DynamicFrame
# import pyspark.sql.functions as F
# from pyspark.sql.types import StringType
# from pyspark.sql.window import Window

# import boto3
# import json

#args_JSON = getResolvedOptions(sys.argv, ["environment_type"])
#environment_type = args_JSON['environment_type']

#if environment_type == 'dev' :
#    catalog_database = 'postgresrds'
#    catalog_table_prefix = 'b2bdevdb'
#else:
#    catalog_database = 'seiubg-rds-b2bds'
#    catalog_table_prefix = 'b2bds'
    

# client10 = boto3.client('secretsmanager')

# response1 = client10.get_secret_value(
#     SecretId='prod/b2bds/rds/system-pipelines'
# )


# database_secrets = json.loads(response1['SecretString'])

# B2B_USER = database_secrets['username']
# B2B_PASSWORD = database_secrets['password']
# B2B_HOST = database_secrets['host']
# B2B_PORT = database_secrets['port']
# B2B_NAME = 'b2bds'



# ## @params: [JOB_NAME]
# args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# sc = SparkContext()
# glueContext = GlueContext(sc)
# spark = glueContext.spark_session
# job = Job(glueContext)
# job.init(args['JOB_NAME'], args)

# credential_df = glueContext.create_dynamic_frame.from_catalog(database = "seiubg-rds-b2bds", table_name = "b2bds_raw_credential_delta", transformation_ctx = "datasource0").toDF()
# newdatasource0 = DynamicFrame.fromDF(credential_df, glueContext, "newdatasource0")
# # Script generated for node ApplyMapping
# ApplyMapping_node2 = ApplyMapping.apply(
#     frame=newdatasource0, mappings=[("credentialtype", "string", "credentialtype", "string"), ("paymentdate", "string", "paymentdate", "string"), ("limitedenglishproficiencyindicator", "string", "limitedenglishproficiencyindicator", "string"), ("credentialstatus", "string", "credentialstatus", "string"), ("primarycredential", "int", "primarycredential", "int"), ("longtermcareworkertype", "string", "longtermcareworkertype", "string"), ("dateofhire", "string", "dateofhire", "string"), ("actiontaken", "string", "actiontaken", "string"), ("excludedlongtermcareworker", "string", "excludedlongtermcareworker", "string"), ("taxid", "int", "taxid", "int"), ("examscheduledsitename", "string", "examscheduledsitename", "string"), ("providernumber", "long", "providernumber", "long"), ("examdtrecdschedtestdate", "string", "examdtrecdschedtestdate", "string"), ("providernamedoh", "string", "providernamedoh", "string"), ("examemailaddress", "string", "examemailaddress", "string"), ("providernamedshs", "string", "providernamedshs", "string"), ("dateofbirth", "string", "dateofbirth", "string"), ("credentiallastdateofcontact", "string", "credentiallastdateofcontact", "string"), ("recordcreateddate", "timestamp", "recordcreateddate", "timestamp"), ("lastissuancedate", "string", "lastissuancedate", "string"), ("examtestertype", "string", "examtestertype", "string"), ("examscheduleddate", "string", "examscheduleddate", "string"), ("phonenum", "string", "phonenum", "string"), ("credentialnumber", "string", "credentialnumber", "string"), ("expirationdate", "string", "expirationdate", "string"), ("lepprovisionalcredential", "string", "lepprovisionalcredential", "string"), ("continuingeducationduedate", "string", "continuingeducationduedate", "string"), ("personid", "long", "personid", "long"), ("examscheduledsitecode", "string", "examscheduledsitecode", "string"), ("lepprovisionalcredentialexpirationdate", "string", "lepprovisionalcredentialexpirationdate", "string"), ("lepprovisionalcredentialissuedate", "string", "lepprovisionalcredentialissuedate", "string"), ("preferredlanguage", "string", "preferredlanguage", "string"), ("firstissuancedate", "string", "firstissuancedate", "string"), ("credentialstatusdate", "string", "credentialstatusdate", "string"), ("nctrainingcompletedate", "string", "nctrainingcompletedate", "string"), ("recordmodifieddate", "timestamp", "recordmodifieddate", "timestamp"), ("dohcertduedate", "date", "dohcertduedate", "date")], transformation_ctx="ApplyMapping_node2")
# ##########################Overwrite script - start ####################################

# final_df = ApplyMapping_node2.toDF()
# #final_df = new_df
# print("final_df count")
# print(final_df.count())

# final_df.show(20,truncate=False)
# final_df.printSchema()

# mode = "overwrite"
# url = "jdbc:postgresql://"+B2B_HOST+"/"+B2B_NAME
# properties = {"user": B2B_USER,"password": B2B_PASSWORD,"driver": "org.postgresql.Driver"}
# final_df.write.option("truncate",True).jdbc(url=url, table="prod.credential", mode=mode, properties=properties)

# print("completed writing")

# ##########################Overwrite script - end ####################################


# job.commit()