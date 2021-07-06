## Imports
import glob
import json
import os
from os.path import splitext,basename
import base64

import cv2
import numpy as np

import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
tf.get_logger().setLevel('ERROR')
from tensorflow import keras
from tensorflow.keras.models  import model_from_json
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.mobilenet_v2 import preprocess_input
from sklearn.preprocessing import LabelEncoder

from local_utils import detect_lp

from fastapi import FastAPI, File, UploadFile

## Processing Functions

#######################################
# Loads a model given a specific path #
#######################################
def load_model(path):
    try:
        path = splitext(path)[0]
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        return model
    except Exception as e:
        print(e)

##############################################################################
# Returns the image of the car (vehicle) and the Licence plate image (LpImg) #
##############################################################################
def get_plate(image_path, Dmax=608, Dmin = 608):
    vehicle = preprocess_image(image_path)
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * Dmin)
    bound_dim = min(side, Dmax)
    _ , LpImg, _, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
    return vehicle, LpImg, cor

######################################################################################
# Converts colors from BGR (as read by OpenCV) to RGB (so that we can display them), #
# also eventually resizes the image to fit the size the model has been trained on    #
######################################################################################
def preprocess_image(image_path,resize=False):
    nparr = np.frombuffer(base64.decodebytes(image_path), dtype=np.uint8)
    img = cv2.imdecode(nparr, -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224,224))
    return img

######################################################
# Grabs the contour of each digit from left to right #
######################################################
def sort_contours(cnts,reverse = False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts

###############################################
# Recognizes a single character from an image #
###############################################
def predict_characters_from_model(image):
    image = cv2.resize(image,(80,80))
    image = np.stack((image,)*3, axis=-1)
    prediction = labels.inverse_transform([np.argmax(character_model.predict(image[np.newaxis,:]))])
    return prediction

####################################################
# Ties all the steps together in a single function #
####################################################
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

    result = ''

    return license_plate_string

## Application

app = FastAPI()

## Model for LP detection
wpod_net_path = "models/wpod-net.json"
wpod_net = load_model(wpod_net_path)
print("[INFO] LP Model loaded successfully...")

## Model for character recoginition
character_net_path = 'models/character_recoginition/MobileNets_character_recognition.json'
character_model = load_model(character_net_path)
print("[INFO] CR Model loaded successfully...")

# Load the character classes
labels = LabelEncoder()
labels.classes_ = np.load('models/character_recoginition/license_character_classes.npy')
print("[INFO] Labels loaded successfully...")

@app.get("/")
async def root():
    return {"message": "Hello World !! Welcome to License Plate Recoginition Service !! Hey RedHat"}


@app.post("/DetectPlate")
async def detect_plate(image: UploadFile = File(...)):
    input_img_bytes = base64.encodebytes(image.file.read())
    license_plate_string = lpr_process(input_img_bytes)
    ## Data is returned to the user
    return  {"lp": license_plate_string}
