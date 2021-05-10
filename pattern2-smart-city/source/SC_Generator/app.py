import boto3
import botocore
import os
import random
import requests
from time import sleep
from io import BytesIO

# Images on local S3
service_point = os.environ['SERVICE_POINT']
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
bucket_name = os.environ['BUCKET_NAME']

# Delay between images
seconds_wait = float(os.environ['SECONDS_WAIT'])

# LPR Service URL
lpr_service = os.environ['LPR_SERVICE_URL']

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
    r = requests.post(url, files=files)
    print(r.content)

# Main loop
while seconds_wait != 0: #This allows the container to keep running but not send any image if parameter is set to 0
    #logging.info("copy image")
    rand_type = random.randint(1,10)
    if rand_type <= 8: # 80% of time, choose randomly
        image_key = car_images[random.randint(0,len(car_images)-1)]
    else: # 20% of time, choose between the first 5 images
        image_key = car_images[random.randint(0,4)]
    send_image(image_key)
    sleep(seconds_wait)

# Dirty hack to keep container running even when no images are to be copied
os.system("tail -f /dev/null")
