import logging
import os
import sys

import boto3
from botocore import UNSIGNED
from botocore.client import Config

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

##############
## Vars init #
##############
# Object storage
access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
service_point = os.environ['SERVICE_POINT']
s3client = boto3.client('s3', 'us-east-1', endpoint_url=service_point,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        use_ssl=True if 'https' in service_point else False)

# Buckets
bucket_source = os.environ['BUCKET_SOURCE']

########
# Code #
########

# Create bucket
s3client.create_bucket(Bucket=bucket_source)

# Populate source images lists
normal_folder = '/opt/app-root/src/xray-data/NORMAL'
pneumonia_folder = '/opt/app-root/src/xray-data/PNEUMONIA'
for img_name in os.listdir(normal_folder):
    s3client.upload_file(normal_folder + '/' + img_name, bucket_source, 'NORMAL/' + img_name)
for img_name in os.listdir(pneumonia_folder):
    s3client.upload_file(pneumonia_folder + '/' + img_name, bucket_source, 'PNEUMONIA/' + img_name)
