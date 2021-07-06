import io
import logging
import os
import gc
import sys
from hashlib import blake2b
from io import BytesIO

import boto3
import numpy as np
import tensorflow as tf
from cloudevents.http import from_http
from flask import Flask, request
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import mysql.connector
from flask_cors import CORS

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

##############
## Vars init #
##############
# Object storage
access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
service_point = os.environ['service_point']
s3client = boto3.client('s3','us-east-1', endpoint_url=service_point,
                       aws_access_key_id = access_key,
                       aws_secret_access_key = secret_key,
                        use_ssl = True if 'https' in service_point else False)

# Bucket base name
bucket_base_name = os.environ['bucket-base-name']

# Helper database
db_user = os.environ['database-user']
db_password = os.environ['database-password']
db_host = os.environ['database-host']
db_db = os.environ['database-db']

# Inference model version
model_version = os.environ['model_version']

########
# Code #
########
# Main Flask app
app = Flask(__name__)
CORS(app)

@app.route("/", methods=["POST"])
def home():
    # Retrieve the CloudEvent
    event = from_http(request.headers, request.get_data())
    
    # Process the event
    process_event(event.data)

    return "", 204

def process_event(data):
    """Main function to process data received by the container image."""

    logging.info(data)
    try:
        # Retrieve event info
        extracted_data = extract_data(data)
        bucket_eventName = extracted_data['bucket_eventName']
        bucket_name = extracted_data['bucket_name']
        img_key = extracted_data['bucket_object']
        img_name = img_key.split('/')[-1]
        logging.info(bucket_eventName + ' ' + bucket_name + ' ' + img_key)

        if 's3:ObjectCreated' in bucket_eventName:
            # Load image and make prediction
            new_image = load_image(bucket_name,img_key)
            result = prediction(new_image)
            logging.info('result=' + result['label'])

            # Get original image and print prediction on it
            image_object = s3client.get_object(Bucket=bucket_name,Key=img_key)
            img = Image.open(BytesIO(image_object['Body'].read()))
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype('FreeMono.ttf', 50)
            draw.text((0, 0), result['label'], (255), font=font)

            # Save image with "-processed" appended to name
            computed_image_key = os.path.splitext(img_key)[0] + '-processed.' + os.path.splitext(img_key)[-1].strip('.')
            buffer = BytesIO()
            img.save(buffer, get_safe_ext(computed_image_key))
            buffer.seek(0)
            sent_data = s3client.put_object(Bucket=bucket_base_name+'-processed', Key=computed_image_key, Body=buffer)
            if sent_data['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise logging.error('Failed to upload image {} to bucket {}'.format(computed_image_key, bucket_base_name + '-processed'))
            update_images_processed(computed_image_key,model_version,result['label'])
            logging.info('Image processed')

            # If "unsure" of prediction, anonymize image
            if (result['pred'] < 0.80 and  result['pred'] > 0.60):
                anonymized_data = anonymize(img,img_name)
                split_key = img_key.rsplit('/', 1)
                if len(split_key) == 1:
                    anonymized_image_key = anonymized_data['anon_img_name']
                else:
                    anonymized_image_key = split_key[0] + '/' + anonymized_data['anon_img_name']
                anonymized_img = anonymized_data['img_anon']
                buffer = BytesIO()
                anonymized_img.save(buffer, get_safe_ext(anonymized_image_key))
                buffer.seek(0)
                sent_data = s3client.put_object(Bucket=bucket_base_name+'-anonymized', Key=anonymized_image_key, Body=buffer)
                if sent_data['ResponseMetadata']['HTTPStatusCode'] != 200:
                    raise logging.error('Failed to upload image {} to bucket {}'.format(anonymized_image_key, bucket_base_name+'-anonymized'))
                update_images_anonymized(anonymized_image_key)
                logging.info('Image anonymized')

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

def extract_data(data):
    logging.info('extract_data')
    record=data['Records'][0]
    bucket_eventName=record['eventName']
    bucket_name=record['s3']['bucket']['name']
    bucket_object=record['s3']['object']['key']
    data_out = {'bucket_eventName':bucket_eventName, 'bucket_name':bucket_name, 'bucket_object':bucket_object}
    return data_out

def load_image(bucket_name, img_path):
    logging.info('load_image')
    logging.info(bucket_name)
    logging.info(img_path)
    obj = s3client.get_object(Bucket=bucket_name, Key=img_path)
    img_stream = io.BytesIO(obj['Body'].read())
    img = tf.keras.preprocessing.image.load_img(img_stream, target_size=(150, 150))
    img_tensor = tf.keras.preprocessing.image.img_to_array(img)                    # (height, width, channels)
    img_tensor = np.expand_dims(img_tensor, axis=0)         # (1, height, width, channels), add a dimension because the model expects this shape: (batch_size, height, width, channels)
    img_tensor /= 255.                                      # imshow expects values in the range [0, 1]

    return img_tensor

def prediction(new_image):
    logging.info('prediction')
    try:
        model = tf.keras.models.load_model('./pneumonia_model.h5')
        logging.info('model loaded')
        pred = model.predict_on_batch(new_image)
        pred_result = pred[0][0].numpy()
        logging.info('prediction made')
        
        if pred_result > 0.80:
            label='Pneumonia, risk=' + str(round(pred_result*100,2)) + '%'
        elif pred_result < 0.60:
            label='Normal, risk=' + str(round(pred_result*100,2)) + '%'
        else:
            label='Unsure, risk=' + str(round(pred_result*100,2)) + '%'
        tf.keras.backend.clear_session()
        gc.collect()
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise   
    logging.info('label')
    prediction = {'label':label,'pred':pred_result}
    return prediction

def anonymize(img,img_name):
    # Use GaussianBlur to blur the PII 5 times.
    logging.info('blurring')
    box = (0, img.size[1]-100, 300, img.size[1])
    crop_img = img.crop(box)
    blur_img = crop_img.filter(ImageFilter.GaussianBlur(radius=5))
    img.paste(blur_img, box)

    # Anonymize filename  
    logging.info('anonymizing filename') 
    prefix = img_name.split('_')[0]
    patient_id = img_name.split('_')[2]
    suffix = img_name.split('_')[-1]
    new_img_name = prefix + '_' + 'XXXXXXXX_' + get_study_id(patient_id) + '_XXXX-XX-XX_' + suffix

    anon_data = {'img_anon': img, 'anon_img_name': new_img_name}

    return anon_data


def get_study_id(patient_id):
    # Given a patient id, returns a study id.
    # In a real implementation this should be replaced by some database lookup.
    # Here we generate a hash based on patient id
    h = blake2b(digest_size=4)
    h.update((int(patient_id)).to_bytes(2, byteorder='big'))
    return h.hexdigest()

def get_safe_ext(key):
    ext = os.path.splitext(key)[-1].strip('.').upper()
    if ext in ['JPG', 'JPEG']:
        return 'JPEG' 
    elif ext in ['PNG']:
        return 'PNG' 
    else:
        logging.error('Extension is invalid')

def update_images_processed(image_name,model_version,label):
    try:
        cnx = mysql.connector.connect(user=db_user, password=db_password,
                                      host=db_host,
                                      database=db_db)
        cursor = cnx.cursor()
        query = 'INSERT INTO images_processed(time,name,model,label) SELECT CURRENT_TIMESTAMP(), "' + image_name + '","' + model_version + '","' + label.split(',')[0] + '";'
        cursor.execute(query)
        cnx.commit()
        cursor.close()
        cnx.close()

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

def update_images_anonymized(image_name):
    try:
        cnx = mysql.connector.connect(user=db_user, password=db_password,
                                      host=db_host,
                                      database=db_db)
        cursor = cnx.cursor()
        query = 'INSERT INTO images_anonymized(time,name) SELECT CURRENT_TIMESTAMP(), "' + image_name + '";'
        cursor.execute(query)
        cnx.commit()
        cursor.close()
        cnx.close()

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise



# Launch Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0')
