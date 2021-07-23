import asyncio, os, time
from aiokafka import AIOKafkaProducer

## global variable :: setting this for kafka producer
KAFKA_ENDPOINT = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'lpr')

async def main():
    
    ### Your business logic Starts Here ###
    message = "This is a sample message"
    time.sleep(30)
    ### Your buiness logic Ends here ###
    
    ## kafka producer initialization
    loop = asyncio.get_event_loop()
    kafkaproducer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_ENDPOINT)
    await kafkaproducer.start()
    try:
        ## Sending message to Kafka Topic and wait for response
        response = await kafkaproducer.send_and_wait(KAFKA_TOPIC, message.encode('utf-8'))
    finally:
        await kafkaproducer.stop()
    print("Success", response)

if __name__ == "__main__":
    asyncio.run(main())
