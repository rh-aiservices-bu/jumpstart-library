import asyncio, os, time
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
        message = "This is a sample message"
        time.sleep(5)
        ### Your buiness logic Ends here ###
        try:
            ## Sending message to Kafka Topic
            response = await kafkaproducer.send_and_wait(KAFKA_TOPIC, message.encode('utf-8'))
            await asyncio.sleep(1)
            print("[producer] Message successfully written to Kafka Topic ...")
            print("[producer] Printing RecordMetadata ...")
            print(response)
            print("------------------------------------------------")
        except asyncio.CancelledError:
            print("[producer] cancelled...")

if __name__ == "__main__":
    asyncio.run(main())
