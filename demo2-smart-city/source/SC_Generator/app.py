import os
import random
import requests
from time import sleep
from io import BytesIO
import asyncio
import uuid
import datetime
import json
import logging

import boto3
import botocore
from aiokafka import AIOKafkaProducer

# Images on local S3
service_point = 'http://' + os.environ['SERVICE_POINT']
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
bucket_name = os.environ['BUCKET_NAME']

## global variable :: setting this for kafka producer
kafka_endpoint = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
kafka_topic_name = os.getenv('KAFKA_TOPIC', 'lpr')

# Delay between images
seconds_wait = float(os.environ['SECONDS_WAIT'])

# LPR Service URL
lpr_service = 'http://' + os.environ['LPR_SERVICE_URL']

# Initialize client
s3client = boto3.client('s3', 'us-east-1', endpoint_url=service_point,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        use_ssl=True if 'https' in service_point else False)

# Initialize images array
car_images=[]
for image in s3client.list_objects(Bucket=bucket_name,Prefix='images/')['Contents']:
    car_images.append(image['Key'])

# Send an image to LPR Service
def send_image(image_key):
    url = lpr_service + '/DetectPlate'
    image_object = s3client.get_object(Bucket=bucket_name,Key=image_key)
    files = {'image': BytesIO(image_object['Body'].read())}
    license_plate_string = json.loads(requests.post(url, files=files).content)['lp']

    if len(license_plate_string) >= 3 :
        rand = random.choices(population=[0,1,2,3,4,5,6,7,8],weights=[0.4, 0.4, 0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],k=1)[0]
        result = {
            "event_timestamp":datetime.datetime.now().isoformat(),
            "event_id": uuid.uuid4().hex,
            "event_vehicle_detected_plate_number": license_plate_string,
            "event_vehicle_lpn_detection_status": "Successful",
            "stationa1": "true" if rand==0 else "false",
            "stationa5201": "true" if rand==1 else "false",
            "stationa13": "true" if rand==2 else "false",
            "stationa2": "true" if rand==3 else "false",
            "stationa23": "true" if rand==4 else "false",
            "stationb313": "true" if rand==5 else "false",
            "stationa4202": "true" if rand==6 else "false",
            "stationa41": "true" if rand==7 else "false",
            "stationb504":  "true" if rand==8 else "false"
        }
    else:
        result = {
            "license_plate_number_detection_status": "Failed",
            "reason": "Not able to read license plate, the input image could be blur or complex for inferencing"
        }
    return json.dumps(result)

async def main():
    ## kafka producer initialization
    loop = asyncio.get_event_loop()
    kafkaproducer = AIOKafkaProducer(loop=loop, bootstrap_servers=kafka_endpoint)
    await kafkaproducer.start()

    # Main loop
    while seconds_wait != 0: #This allows the container to keep running but not send any image if parameter is set to 0
        rand_type = random.randint(1,10) # Random cheater...
        if rand_type <= 8: # 80% of time, choose randomly
            image_key = car_images[random.randint(0,len(car_images)-1)]
        else: # 20% of time, choose between the first 5 images only
            image_key = car_images[random.randint(0,4)]

        try:
            result = send_image(image_key) # Get generated licence plate info

            ## Send the data to Kafka
            await kafkaproducer.send_and_wait(kafka_topic_name, result.encode('utf-8'))
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

        sleep(seconds_wait)

asyncio.run(main())

# Dirty hack to keep container running even when no images are to be copied
os.system("tail -f /dev/null")
