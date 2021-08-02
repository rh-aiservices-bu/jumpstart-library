import asyncio, os, time
from aiokafka import AIOKafkaProducer

## global variable :: setting this for kafka producer
KAFKA_ENDPOINT = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'lpr')

async def main():
    
    ### Your business logic Starts Here ###
    message = "This is a sample message"
    time.sleep(5)
    ### Your buiness logic Ends here ###
    
    ## kafka producer initialization
    kafkaproducer = AIOKafkaProducer(loop=asyncio.get_event_loop(), bootstrap_servers=KAFKA_ENDPOINT)
    print("[producer] starting...")
    await kafkaproducer.start()
    try:
        ## Sending message to Kafka Topic and wait for response
        print("[producer] sending msg...")
        response = await kafkaproducer.send_and_wait(KAFKA_TOPIC, message.encode('utf-8'))
    except asyncio.CancelledError:
        print("[producer] cancelled...")
    finally:
        print("[producer] stopping...")
        await kafkaproducer.stop()
        print("[producer] stopped")
    
    print("------- Message successfully written to Kafka Topic -------")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
