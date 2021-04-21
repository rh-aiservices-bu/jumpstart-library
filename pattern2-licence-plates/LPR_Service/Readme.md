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

## Automated Builds
```
oc new-project license-plate-recognition
# Login to quay.io > account > get password > docker configuration file
oc create secret generic quayio-registry --from-file .dockerconfigjson=/Users/karasing/Downloads/karasing-auth.json --type kubernetes.io/dockerconfigjson
oc secrets link builder quayio-registry

oc new-app --as-deployment-config --name=license-plate-recognition https://github.com/red-hat-data-services/jumpstart-library.git#ksingh-tf-v1 --context-dir=pattern2-licence-plates/LPR_Service -e KAFKA_ENDPOINT='pattern-2-kafka-kafka-bootstrap:9092 ' -e KAFKA_TOPIC='lpr' 

oc expose service/license-plate-recognition


bin/kafka-console-consumer.sh --bootstrap-server pattern-2-kafka-kafka-bootstrap:9092 --topic lpr --from-beginning


```

## Deploy the service on OCP

```
oc new-project license-plate-recognition
oc adm policy add-scc-to-user anyuid -z default
oc new-app --docker-image=quay.io/xxx/license-plate-recognition-app --name=license-plate-recognition
oc expose service/license-plate-recognition
oc get all
```
```

oc new-app --name license-plate-recognition2 --as-deployment-config https://github.com/red-hat-data-services/jumpstart-library#ksingh-tf-v1 --context-dir=pattern2-licence-plates/LPR_Service -l app=license-plate-recognition2 -e KAFKA_ENDPOINT=pattern-2-kafka-kafka-bootstrap:9092

oc adm policy add-scc-to-user anyuid -z default
oc scale dc/license-plate-recognition2 --replicas=2
oc expose service/license-plate-recognition2

oc set env dc/license-plate-recognition2  -e KAFKA_ENDPOINT=pattern-2-kafka-kafka-bootstrap:9092

./lprctl --endpoint http://license-plate-recognition-license-plate-recognition2.apps.perf3.chris.ocs.ninja  

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

### Local Testing (for development)

```
cd jumpstart-library/pattern2-licence-plates/LPR_Service
docker run  -d -p 80:80 lpr-service
time curl -X 'POST' http://127.0.0.1/DetectPlate -F 'image=@dataset/images/Cars0.png'
``` 

```
### Local Testing
before : 0.00s user 0.00s system 0% cpu 24.580 total
after : 0.00s user 0.00s system 1% cpu 0.562 total

### Server Testing
before : 0.01s user 0.01s system 0% cpu 24.508 total
after : 
```

### Kafka Setup on local

```
docker network create kafka-net --driver bridge

docker run --rm --name zookeeper-server -p 2181:2181 -d --network kafka-net -e ALLOW_ANONYMOUS_LOGIN=yes bitnami/zookeeper:latest

nc -v localhost 2181

docker run --rm --name kafka-server1 -d --network kafka-net -e ALLOW_PLAINTEXT_LISTENER=yes -e KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181 -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 -p 9092:9092 bitnami/kafka:latest

curl https://raw.githubusercontent.com/birdayz/kaf/master/godownloader.sh | BINDIR=$HOME/bin bash
sudo cp /Users/karasing/bin/kaf /usr/local/bin/kaf

kaf config add-cluster local -b localhost:9092
kaf config select-cluster
kaf node ls

kaf topics
kaf topic create lpr
kaf topic describe lpr
echo test | kaf produce lpr
kaf topic describe lpr
kaf consume lpr
```