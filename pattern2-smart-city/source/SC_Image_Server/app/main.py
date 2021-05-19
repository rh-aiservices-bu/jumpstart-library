import os
from string import Template
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from fastapi import FastAPI

from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base


###################################### Patch code

import boto3
import botocore
import random

# Images on local S3
service_point = os.environ['SERVICE_POINT']
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
bucket_name = os.environ['BUCKET_NAME']

# Initialize client
s3client = boto3.client('s3', 'us-east-1', endpoint_url=service_point,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        use_ssl=True if 'https' in service_point else False)

# Initialize images array
car_images=[]
for image in s3client.list_objects(Bucket=bucket_name,Prefix='images/')['Contents']:
    car_images.append(image['Key'])

def get_random_image():
    """Retrieves the last uploaded image according to helper database timestamp."""

    try:
        image_key = car_images[random.randint(0,len(car_images)-1)]

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    return image_key

##################################

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HT@1202k')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_NAME = os.getenv('TABLE_NAME','event')

engine = create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})

Base = declarative_base()

class Event(Base):
    __tablename__ = "event"
    event_id = Column(String, primary_key=True, index=True)
    event_timestamp = Column('date', DateTime(timezone=True), default=func.now())
    event_vehicle_detected_plate_number = Column(String, index=True)
    event_vehicle_lpn_detection_status = Column(String)
    stationa1 = Column(Boolean, unique=False)
    stationa5201 = Column(Boolean, unique=False)
    stationa13 = Column(Boolean, unique=False)
    stationa2 = Column(Boolean, unique=False)
    stationa23 = Column(Boolean, unique=False)
    stationb313 = Column(Boolean, unique=False)
    stationa4202 = Column(Boolean, unique=False)
    stationa41 = Column(Boolean, unique=False)
    stationb504 = Column(Boolean, unique=False)


def get_last_image():
    """Retrieves the last uploaded image according to helper database timestamp."""

    try:
        connection = engine.connect()
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    return result

# Response templates 
LOCATION_TEMPLATE = Template("""<img src="${service_point}/${bucket_name}/${image_name}" style="width:300px;"></img>""")

## Application  

app = FastAPI()

@app.get("/last_image")
async def last_image():
    image_name = get_last_image()   
    if image_name != "":   
        html = LOCATION_TEMPLATE.substitute(service_point=service_point, bucket_name=bucket_name, image_name=image_name)
    else:
        html = '<h2 style="font-family: Roboto,Helvetica Neue,Arial,sans-serif;text-align: center; color: white;font-size: 15px;font-weight: 400;">No image to show</h2>'
    return html

@app.get("/random_image")
async def random_image():
    image_name = get_random_image()   
    if image_name != "":   
        html = LOCATION_TEMPLATE.substitute(service_point=service_point, bucket_name=bucket_name, image_name=image_name)
    else:
        html = '<h2 style="font-family: Roboto,Helvetica Neue,Arial,sans-serif;text-align: center; color: white;font-size: 15px;font-weight: 400;">No image to show</h2>'
    return html