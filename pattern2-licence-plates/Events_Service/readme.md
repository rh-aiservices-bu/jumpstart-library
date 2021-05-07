### Prerequisite
- kafka Core , Mirror maker and Kafka edge should be up and running
- use kafak core bootstrap endopints

```
oc new-app --name events-service --as-deployment-config python:3.8~https://github.com/red-hat-data-services/jumpstart-library#ksingh-tf-v1 --context-dir=pattern2-licence-plates/Events_Service -l app=events-service -e KAFKA_ENDPOINT=kafka-core-site-kafka-bootstrap.lpr-core-site.svc.cluster.local:9092 -e KAFKA_TOPIC=lpr -e KAFKA_CONSUMER_GROUP_ID=event_consumer_group -e DB_USER=dbadmin -e DB_PASSWORD='HT@1202k' -e DB_HOST=postgresql DB_NAME=pgdb -e TABLE_NAME=event

oc set env dc/events-service  -e KAFKA_ENDPOINT=kafka-core-site-kafka-bootstrap.lpr-core-site.svc.cluster.local:9092 

```