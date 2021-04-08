#!/usr/bin/python

import requests
import base64
import json

results = {}

# Sample image file is available at http://plates.openalpr.com/ea7the.jpg
# IMAGE_PATH = '/tmp/sample.jpg'
# SECRET_KEY = 'sk_17815f570223fef0152ffbba'

# with open(IMAGE_PATH, 'rb') as image_file:
#     img_base64 = base64.b64encode(image_file.read())

# url = 'https://api.openalpr.com/v3/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % (SECRET_KEY)
# r = requests.post(url, data = img_base64)

# print(json.dumps(r.json(), indent=2))

file = open("dump.json")
data  = json.load(file)

for i in data["results"]:
  #print(i['plate'])
  #results.update({"plate_number": i['plate']})
  #results.update({"region": i['region']})
  #results.update({"color": i['color[0]']})
  print(type(i["vehicle"]))
  print(i["vehicle"])
file.close
print(results)