from aiokafka import AIOKafkaProducer
import asyncio

loop = asyncio.get_event_loop()

async def send_one():
    producer = AIOKafkaProducer(
        loop=loop, bootstrap_servers='localhost:9092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        await producer.send_and_wait("lpr", b"Yo You karan Singh")
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()

loop.run_until_complete(send_one())