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

bin/kafka-console-consumer.sh --bootstrap-server kafka-core-site-kafka-bootstrap:9092 --topic lpr


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
oc adm policy add-scc-to-user anyuid -z default # used for tiangolo/uvicorn-gunicorn-fastapi:python3.8 image 

oc new-app --name license-plate-recognition --as-deployment-config https://github.com/red-hat-data-services/jumpstart-library#ksingh-tf-v1 --context-dir=pattern2-licence-plates/LPR_Service -l app=license-plate-recognition -e KAFKA_ENDPOINT=pattern-2-kafka-kafka-bootstrap:9092

oc scale dc/license-plate-recognition --replicas=2
oc expose service/license-plate-recognition


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

### Testing the overall flow

```
git clone https://github.com/red-hat-data-services/jumpstart-library.git
cd jumpstart-library
git checkout ksingh-tf-v1
cd pattern2-licence-plates/LPR_Service/dataset/images
## This is our images dataset
ls
curl -X 'POST' http://license-plate-recognition2-license-plate-recognition.apps.perf3.chris.ocs.ninja/DetectPlate -F "@image=1.png"
oc get po -l deploymentconfig=postgresql
oc port-forward postgresql-1-d6h9t 5432:5432
psql -h 127.0.0.1 -p 5432 -U dbadmin -w HT@1202k -d pgdb
\d
\d event;
\d vehicle_metadata;
select * from event; 
```
## Secor Notes
```
oc create -f <obc.yaml>
oc get obc secor-bucket  -o jsonpath='{.spec.bucketName}'

oc get secret secor-bucket --template={{.data.AWS_ACCESS_KEY_ID}} | base64 -d 
oc get secret secor-bucket --template={{.data.AWS_SECRET_ACCESS_KEY}} | base64 -d

oc rsh s3cmd

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)" ls 

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)" put /s3cmd-2.1.0.zip s3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/s3cmd.zip

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)" ls s3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)
" ls s3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/lpr/offset=0/

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)
" ls s3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/lpr/offset=0/1_0_00000000000000440962

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)
" get s3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/lpr/offset=0/1_0_00000000000000440962  car.txt


oc project lpr-core-site

```

## SuperSet Notes
admin/admin

oc new-app --name postgresql-db --template=postgresql-ephemeral  -p POSTGRESQL_USER=dbadmin -p POSTGRESQL_PASSWORD=HTb1202k -p POSTGRESQL_DATABASE=pgdb

postgresql://'dbadmin':'HTt1202k'@postgresql/pgdb

## Deploying Presto
brew install helm
oc new-project presto-1

git clone https://github.com/valeriano-manassero/helm-charts.git
cd helm-charts
vim valeriano-manassero/trino/values.yaml
service:worker:1
oc adm policy add-scc-to-user anyuid -z default
helm install my-trino valeriano-manassero/trino --version 1.1.1


```
+ NODE_ID=-Dnode.id=my-trino-worker-7bcbf5664-9xv7t
+ exec /usr/lib/trino/bin/launcher run --etc-dir /etc/trino -Dnode.id=my-trino-worker-7bcbf5664-9xv7t
ERROR: [Errno 13] Permission denied: '/data/trino/var'
```


oc port-forward svc/my-trino 8080:8080
visit http://127.0.0.1:8080


ALTER USER postgres WITH PASSWORD 'postgres';

connector.name=postgresql
connection-url=jdbc:postgresql://postgresql.license-plate-recognition.svc.cluster.local:5432/presto
connection-user=postgres
connection-password=postgres


  hive:
    additionalProperties: |
      connector.name=hive-hadoop2
      hive.s3.endpoint=http://172.30.197.73
      hive.s3.signer-type=S3SignerType
      hive.s3.path-style-access=true
      hive.s3.staging-directory=/tmp
      hive.s3.ssl.enabled=false
      hive.s3.sse.enabled=false

postgresql://dbadmin:HT%401202k@postgresql.license-plate-recognition.svc.cluster.local/pgdb
postgresql://postgres:postgres@postgresql.license-plate-recognition.svc.cluster.local/presto

presto://my-trino.presto-1.svc.cluster.local:8080/postgresql

