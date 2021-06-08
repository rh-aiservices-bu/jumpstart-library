import os
from string import Template
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from sqlalchemy import create_engine,MetaData
import sqlalchemy as db


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

engine = db.create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})
connection = engine.connect()
metadata = db.MetaData()

event = db.Table('event',metadata, autoload=True, autoload_with=engine)

def get_last_image():
    """Retrieves the last uploaded image according to helper database timestamp."""

    try:
        query = """SELECT e.event_vehicle_detected_plate_number,
                    e.date,
                    v.vehicle_make,
                    v.vehicle_color,
                    v.vehicle_body_type ,
                    v.vehicle_owner_name,
                    v.metadata_image_name
                    FROM event  AS e
                    LEFT JOIN vehicle_metadata AS v
                    ON e.event_vehicle_detected_plate_number = v.vehicle_registered_plate_number
                    ORDER by e.date DESC
                    LIMIT 1"""
        rs = connection.execute(query).fetchall()
        for row in rs:
            row_as_dict = dict(row)
            result = row_as_dict["metadata_image_name"]
        
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

@app.get("/random_image", response_class=HTMLResponse)
async def random_image():
    image_name = get_random_image()   
    if image_name != "":   
        html = LOCATION_TEMPLATE.substitute(service_point=service_point, bucket_name=bucket_name, image_name=image_name)
    else:
        html = '<h2 style="font-family: Roboto,Helvetica Neue,Arial,sans-serif;text-align: center; color: white;font-size: 15px;font-weight: 400;">No image to show</h2>'
    return html

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
    )