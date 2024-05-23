#DT-824 : Remove Smartsheet Course Completions from E2E Process

'''import requests
import zipfile
import json
import io, os
import sys
import re
import boto3
import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.context import SparkContext
from pyspark.sql.functions import first
import time
import pandas 
import datetime
from dateutil.rrule import rrule, MONTHLY

id_list = []

suffix_list = []

s3_client = boto3.client('s3',region_name='us-west-2')

DF_list = []

# Accessing the Secrets Manager from boto3 lib
ssm_client = boto3.client('secretsmanager')
s3_client = boto3.client('s3',region_name='us-west-2')
response = ssm_client.get_secret_value(
    SecretId='prod/smartsheet/glue'
)

secrets = json.loads(response['SecretString'])
ss_api_key = secrets['ss_api_key']

url = 'https://api.smartsheet.com/2.0/reports/?includeAll=true'

start_date = datetime.datetime.strptime("01-01-2021", "%d-%m-%Y")
end_date = datetime.datetime.today()
month_list = []
date_generated = [dt for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]
for date in date_generated:
    month_list.append(date.strftime("%m%Y"))
    
print('months chosen')
print(str(month_list))


def upload_to_s3(data):
    
    time.sleep(1)
    today = datetime.datetime.now()
    suffix = today.strftime("%Y%m%d%H%M%S")
    print(suffix)
    
    k_end = 'Inbound/raw/smartsheets/raw/SmartSheet'+suffix+'.csv'
    s3_client.put_object(Body=data, Bucket='seiubg-b2bds-prod-feeds-fp7mk', Key=k_end)
    suffix_list.append(suffix)
    print('raw data ingested')

def callMyApi():
    
    print ("Calling API ...")
    
    try:
        
        res = requests.get(url,headers={'Authorization': 'Bearer ' + ss_api_key,'Content-Type': 'application/csv'})
        print("CSV to JSON...")
        data = json.loads(res.content, encoding='utf-8')
        for i in data['data']:
            if 'Timothy' in i['name']:
                if i['name'][19:25] in month_list:
                    id_list.append(i['id'])
        print('ids extracted from reports request')
        print(str(id_list))
        
        for rid in id_list:
            rurl = 'https://api.smartsheet.com/2.0/reports/'+str(rid)+'?includeAll=true'
            res = requests.get(rurl,headers={'Authorization': 'Bearer ' + ss_api_key, 'Accept': 'text/csv'})
            upload_to_s3(res.content)

        print('json done.')

    except Exception as e:
        
        print(e)

def flatten(smartsheetDF):
    
    smartsheetDF2 = smartsheetDF.withColumn("columns_exploded", F.explode("columns")).withColumn("rows_exploded", F.explode("rows"))
    smartsheetDF3 = smartsheetDF2.select("rows_exploded.*", "columns_exploded.*")
    smartsheetDF4 = smartsheetDF3.select("virtualid","title")
    smartsheetDF5 = smartsheetDF4.distinct()
    smartsheetDF6 = smartsheetDF3.withColumn("cells_explode", F.explode("cells"))
    smartsheetDF7 = smartsheetDF6.select("cells_explode.value",'cells_explode.virtualColumnId','rowNumber')
    joinDF = smartsheetDF5.join(smartsheetDF7,smartsheetDF5["virtualid"] == smartsheetDF7["virtualColumnId"] ,how="inner")
    reshaped_df = joinDF.groupby(joinDF.rowNumber).pivot("title").agg(first("value"))
    
    return reshaped_df.coalesce(1)

def smartsheet(spark):
    
    print('loading raw for flattening')
    
    for s in suffix_list:
        smartsheetDF = spark.read.format("csv").option("header","true").option("InferSchema","true").load("s3://seiubg-b2bds-prod-feeds-fp7mk/Inbound/raw/smartsheets/raw/SmartSheet"+s+".csv")
        DF_list.append(smartsheetDF)
    
    #print(str(DF_list))
    
    if len(DF_list) != 0:
        outputDF = DF_list[0]

        for n in range(len(DF_list)):
            if n != 0:
                outputDF = outputDF.union(DF_list[n])
    
        print ("Putting curated in S3")
    

        pandas_df = outputDF.toPandas()
        pandas_df.to_csv("s3://seiubg-b2bds-prod-feeds-fp7mk/Inbound/raw/smartsheets/curated/SmartSheet"+suffix_list[0]+".csv", header=True, index=None, sep=',', mode='a')
        print('Curated data has been ingested in s3')
    else:
        print('no raw data found')
    
def main():
    
    spark = SparkSession \
	      .builder \
	      .master("local") \
	      .enableHiveSupport()\
	      .appName("Smartsheet") \
	      .getOrCreate()
	      
    spark.sparkContext.setLogLevel("ERROR")
    print('spark session has been created...')
    
    callMyApi()
    
    smartsheet(spark)
    


if __name__ == "__main__": 
    main()
    
'''
