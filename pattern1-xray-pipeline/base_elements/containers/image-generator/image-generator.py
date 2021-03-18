import logging
import os
import random
import sys
from time import sleep

import boto3
import mysql.connector
import requests
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

s3sourceclient = boto3.client('s3', config=Config(signature_version=UNSIGNED))

# Buckets
bucket_source = os.environ['BUCKET_SOURCE']
bucket_source_name = bucket_source.split('/')[-1]
bucket_destination = os.environ['BUCKET_BASE_NAME']

# Helper database
db_user = os.environ['DATABASE_USER']
db_password = os.environ['DATABASE_PASSWORD']
db_host = os.environ['DATABASE_HOST']
db_db = os.environ['DATABASE_DB']

# Delay between images
seconds_wait = float(os.environ['SECONDS_WAIT'])

########
# Code #
########
def copy_file(source, image_key, destination, image_name):
    """Copies an object from a URL source to a destination bucket.""" 

    image_url = source + '/' + image_key
    req_for_file = requests.get(image_url, stream=True)

    # Init File-like object (to be used by upload_fileobj method)
    file_object_from_req = req_for_file.raw

    s3client.upload_fileobj(file_object_from_req,destination,image_name)

def update_images_uploaded(image_name):
    """Inserts image name and timestamp into the helper database."""

    try:
        cnx = mysql.connector.connect(user=db_user, password=db_password,
                                      host=db_host,
                                      database=db_db)
        cursor = cnx.cursor()
        query = 'INSERT INTO images_uploaded(time,name) SELECT CURRENT_TIMESTAMP(),"' + image_name + '";'
        cursor.execute(query)
        cnx.commit()
        cursor.close()
        cnx.close()

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

# Populate source images lists
pneumonia_images=[]
for image in s3sourceclient.list_objects(Bucket=bucket_source_name,Prefix='PNEUMONIA/')['Contents']:
    pneumonia_images.append(image['Key'])
normal_images=[]
for image in s3sourceclient.list_objects(Bucket=bucket_source_name,Prefix='NORMAL/')['Contents']:
    normal_images.append(image['Key'])

# Main loop
while seconds_wait != 0: #This allows the container to keep running but not send any image if parameter is set to 0
    logging.info("copy image")
    rand_type = random.randint(1,10)
    if rand_type <= 8: # 80% of time, choose a normal image
        image_key = normal_images[random.randint(0,len(normal_images)-1)]
    else:
        image_key = pneumonia_images[random.randint(0,len(pneumonia_images)-1)]
    image_name = image_key.split('/')[-1]
    copy_file(bucket_source,image_key,bucket_destination,image_name)
    update_images_uploaded(image_name)
    sleep(seconds_wait)

# Dirty hack to keep container running even when no images are to be copied
os.system("tail -f /dev/null")
