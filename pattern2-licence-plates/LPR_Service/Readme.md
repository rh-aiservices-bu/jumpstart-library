## Introduction

This is a License Plate Recoginition service that provides a REST endpoint to detect license plate and reads that, and in response provides the license plate number.

## Building the App

- Clone the master repository and navigat to the LPR_Service directory

```
docker build -t lpr-service .
docker login -u="xxx" -p="xxx" quay.io
docker tag lpr-service quay.io/xxx/license-plate-recognition-app:latest
docker push quay.io/xxx/license-plate-recognition-app
```
## Deploy the service on OCP

```
oc new-project license-plate-recognition
oc adm policy add-scc-to-user anyuid -z default
oc new-app --docker-image=quay.io/xxx/license-plate-recognition-app --name=license-plate-recognition
oc expose service/license-plate-recognition
oc get all
```
## Test the service

```
curl http://license-plate-recognition-license-plate-recognition.apps.perf3.chris.ocs.ninja
```
Sample response
```
{"message":"Hello World ! Welcome to License Plate Recoginition Service.."}
```

## Testing License Plate Recoginition

- Use the sample images dataset provided in this git repo
- Navigate to ``jumpstart-library/pattern2-licence-plates/LPR_Service/dataset/images`` , pickup the images and perform LPR
  
```
curl -X 'POST' http://license-plate-recognition-license-plate-recognition.apps.perf3.chris.ocs.ninja/DetectPlate -F 'image=@Cars0.png'
```
Sample Response
```
{"license_plate_number_detection_status":"Successful","detected_license_plate_number":"LCA2555"}
```

## 