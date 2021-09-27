import asyncio, os, time, json
from aiokafka import AIOKafkaProducer

## Global Variables to define Kafka Endpoint and Kafka Topic
KAFKA_ENDPOINT = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'lpr')

async def main():
    ## kafka producer initialization
    kafkaproducer = AIOKafkaProducer(bootstrap_servers=KAFKA_ENDPOINT)
    print("------ Starting Kafka Producer ------")
    await kafkaproducer.start()
    while True:
        ### Your business logic Starts Here ###
        #message = "This is a sample message"
        message = {
        "event_timestamp": "2021-09-21T19:51:32.903077",
        "event_id": "3aa9152d70f543e7bbe61bfa1d62d0e7",
        "event_vehicle_detected_plate_number": "DAN54P",
        "event_vehicle_lpn_detection_status": "Successful",
        "stationa1": "true",
        "stationa5201": "false",
        "stationa13": "false",
        "stationa2": "false",
        "stationa23": "false",
        "stationb313": "false",
        "stationa4202": "false",
        "stationa41": "false",
        "stationb504": "false"
        }
        time.sleep(5)
        ### Your buiness logic Ends here ###
        try:
            ## Sending message to Kafka Topic
            response = await kafkaproducer.send_and_wait(KAFKA_TOPIC, json.dumps(message).encode('utf-8'))
            await asyncio.sleep(1)
            print("[producer] Message successfully written to Kafka Topic ...")
            print("[producer] Printing RecordMetadata ...")
            print(response)
            print("------------------------------------------------")
        except asyncio.CancelledError:
            print("[producer] cancelled...")

if __name__ == "__main__":
    asyncio.run(main())
