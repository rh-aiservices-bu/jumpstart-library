import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.get_logger().setLevel('ERROR')
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from local_utils import detect_lp
from os.path import splitext,basename
from tensorflow.keras.models  import model_from_json
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras
import glob
import os
import json
from fastapi import FastAPI, File, UploadFile
import base64
import requests
import datetime
import random
#from faker import Faker
from aiokafka import AIOKafkaProducer
import asyncio



def save_model_h5_to_tf_format(path):
    try:
        path = splitext(path)[0]
        #print(splitext(path.split('/')[0]))
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        #print(os.path())
        # Save the model to h5 format
        model.save("models/wpod_net_all_in_one.h5")
        #print("Keras Model Saved successfully as h5 format")
        model = tf.keras.models.load_model('models/wpod_net_all_in_one.h5')
        # Save the model to TF SavedModel format
        tf.saved_model.save(model, "models")
        #print("successfully saved keras model h5 file to tensorflow SavedModel format")
        return 
    except Exception as e:
        print(e)

def get_plate(image_path, Dmax=608, Dmin = 608):
    vehicle = preprocess_image(image_path)
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * Dmin)
    bound_dim = min(side, Dmax)
    _ , LpImg, _, cor = detect_lp(tf_model, vehicle, bound_dim, lp_threshold=0.5)
    return vehicle, LpImg, cor

def preprocess_image(image_path,resize=False):
    nparr = np.frombuffer(base64.decodebytes(image_path), dtype=np.uint8)
    img = cv2.imdecode(nparr, -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224,224))
    return img

# Create sort_contours() function to grab the contour of each digit from left to right 
def sort_contours(cnts,reverse = False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts

# pre-processing input images and pedict with model
def predict_characters_from_model(image):
    image = cv2.resize(image,(80,80))
    image = np.stack((image,)*3, axis=-1)
    prediction = labels.inverse_transform([np.argmax(model.predict(image[np.newaxis,:]))])
    return prediction


def  lpr_process(input_image_path):
    license_plate_string =  ""
    vehicle, LpImg, cor = get_plate(input_image_path)
    if  len(LpImg) > 0:
        plate_image = cv2.convertScaleAbs(LpImg[0], alpha=(255.0))
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(7,7),0)
         # Applied inversed thresh_binary 
        binary = cv2.threshold(blur, 180, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)
        
        cont, _  = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # creat a copy version "test_roi" of plat_image to draw bounding box
        test_roi = plate_image.copy()
        # Initialize a list which will be used to append charater image
        crop_characters = []
        
        # define standard width and height of character
        digit_w, digit_h = 30, 60
        
        for c in sort_contours(cont):
            (x, y, w, h) = cv2.boundingRect(c)
            ratio = h/w
            if 1<=ratio<=3.5: # Only select contour with defined ratio
                if h/plate_image.shape[0]>=0.5: # Select contour which has the height larger than 50% of the plate
                    # Draw bounding box arroung digit number
                    cv2.rectangle(test_roi, (x, y), (x + w, y + h), (0, 255,0), 2)
                    # Sperate number and gibe prediction
                    curr_num = thre_mor[y:y+h,x:x+w]
                    curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                    _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                    crop_characters.append(curr_num)
        
        cols = len(crop_characters)
        
        for i,character in enumerate(crop_characters):
            title = np.array2string(predict_characters_from_model(character))
            license_plate_string+=title.strip("'[]")

    else:
        license_plate_string =  ""
        
    if len(license_plate_string) >= 3 :
       # fake = Faker(['en-US', 'en_US', 'en_US', 'en-US'])
        rand = random.randint(0,len(location_data)-1)
        result = {
            "event_timestamp": str(datetime.datetime.now()),
            "event_id": str(random.randint(99,99999)),
             "event_vehicle_detected_plate_number": license_plate_string,
            "event_vehicle_detected_lat": str(location_data[rand]['lat']),
            "event_vehicle_detected_long": str(location_data[rand]['long']),
            "event_vehicle_lpn_detection_status": "Successful"
        }
        #print(json.dumps(result))
        #print("mv "+ input_image_path +" dataset/images/success")
        # event_vehicle_captured_image
        # event_vehicle_detected_geo_location
        return result
    else:
        result = {
            "license_plate_number_detection_status": "Failed",
            "reason": "Not able to read license plate, it could be blur or complex image"
        }
        #print(json.dumps(result))
        return result

# def main():
#     wpod_net_path = "models/wpod-net.json"
#     save_model_h5_to_tf_format(wpod_net_path)
    # Just provide the directory name where the TF *.pb (model file saved_model.pb) file is located
    

   # input_image_path = "dataset/plate5.jpeg"
    
    # for image_id in range(0,11):
    #     input_image_path = "dataset/Cars" + str(image_id) + ".png"
    #     license_plate_string = lpr_process(input_image_path)

    # dataset_directory = r'dataset/images'
    # for entry in os.scandir(dataset_directory):
    #     if (entry.path.endswith(".jpg")
    #            or entry.path.endswith(".png") or entry.path.endswith(".jpeg")) and entry.is_file():
    #        license_plate_string = lpr_process(entry.path)
   
# if __name__ == "__main__":
#     tf_model = keras.models.load_model('models')
#     main()



app = FastAPI()

## Model for LP detection
wpod_net_path = "models/wpod-net.json"
save_model_h5_to_tf_format(wpod_net_path)
tf_model = keras.models.load_model('models')

## Model for character recoginition
json_file = open('models/character_recoginition/MobileNets_character_recognition.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
model.load_weights("models/character_recoginition/License_character_recognition_weight.h5")
labels = LabelEncoder()
labels.classes_ = np.load('models/character_recoginition/license_character_classes.npy')

## Location Data Lat and Long
location_data = json.load(open("location_data.json"))

## global variable :: setting this for kafka producer
kafka_endpoint = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
kafka_topic_name = os.getenv('KAFKA_TOPIC', 'lpr')

## kafka producer initilization
loop = asyncio.get_event_loop()
kafkaproducer = AIOKafkaProducer(loop=loop, bootstrap_servers=kafka_endpoint)

@app.on_event("startup")
async def startup_event():
    await kafkaproducer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await kafkaproducer.stop()


@app.get("/")
async def root():
    return {"message": "Hello World !! Welcome to License Plate Recoginition Service.."}

# @app.get("/DetectPlate")
# async def detect_plate():
#     input_image_path = "dataset/images/Cars0.png"
#     license_plate_string = lpr_process(input_image_path)
#     return  license_plate_string

@app.post("/DetectPlate")
async def detect_plate(image: UploadFile = File(...)):
    input_imag_bytes =base64.encodebytes(image.file.read())
    license_plate_string = lpr_process(input_imag_bytes)
    return  license_plate_string

@app.post("/DetectPlateFromUrl/")
async def DetectPlateFromUrl(url: str):    
    input_imag_bytes = base64.encodebytes(requests.get(url).content)
    license_plate_string = lpr_process(input_imag_bytes)
    await kafkaproducer.send_and_wait(kafka_topic_name, json.dumps(license_plate_string).encode('utf-8'))
    return  license_plate_string