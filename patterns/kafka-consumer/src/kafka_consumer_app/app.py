import asyncio, os, time
from aiokafka import AIOKafkaConsumer

## Global Variables to define Kafka Endpoint and Kafka Topic
KAFKA_ENDPOINT = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'lpr')

async def main():
    ## kafka consumer initialization
    kafkaconsumer= AIOKafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_ENDPOINT, group_id="consumer-group-1")
    print("------ Starting Kafka Consumer------")
    await kafkaconsumer.start()
    try:
        # Consume messages
        async for msg in kafkaconsumer:
            print("Consumed Message: ", msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await kafkaconsumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
