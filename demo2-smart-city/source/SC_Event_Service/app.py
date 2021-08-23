from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from aiokafka import AIOKafkaConsumer
import asyncio, os, ast , sys
import nest_asyncio
nest_asyncio.apply()

## global variable :: setting this for kafka Consumer
KAFKA_ENDPOINT = os.getenv('KAFKA_ENDPOINT', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'lpr')
KAFKA_CONSUMER_GROUP_ID = os.getenv('KAFKA_CONSUMER_GROUP_ID', 'event_consumer_group')
loop = asyncio.get_event_loop()

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HT@1202k')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_NAME = os.getenv('TABLE_NAME','event')

Base = declarative_base()
class Event(Base):
    __tablename__ = "event"
    event_id = Column(String, primary_key=True, index=True)
    event_timestamp = Column('date', DateTime(timezone=True), default=func.now())
    event_vehicle_detected_plate_number = Column(String, index=True)
    event_vehicle_lpn_detection_status = Column(String)
    stationa1 = Column(Boolean, unique=False)
    stationa5201 = Column(Boolean, unique=False)
    stationa13 = Column(Boolean, unique=False)
    stationa2 = Column(Boolean, unique=False)
    stationa23 = Column(Boolean, unique=False)
    stationb313 = Column(Boolean, unique=False)
    stationa4202 = Column(Boolean, unique=False)
    stationa41 = Column(Boolean, unique=False)
    stationb504 = Column(Boolean, unique=False)

async def consume():
    engine = create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME+'?tcp_user_timeout=3000&connect_timeout=10', pool_pre_ping=True, connect_args={})
    connection = engine.connect()

    kafkaConsumer = AIOKafkaConsumer(KAFKA_TOPIC, loop=loop, bootstrap_servers=KAFKA_ENDPOINT, group_id=KAFKA_CONSUMER_GROUP_ID)

    ## Create Table if does not exists
    Event.__table__.create(bind=engine, checkfirst=True)

    await kafkaConsumer.start()
    try:
        async for msg in kafkaConsumer:
            print(msg.key)
            message = msg.value
            payload=ast.literal_eval(message.decode('utf-8'))
            try:
                connection.execute(f"""INSERT INTO public.{TABLE_NAME}(event_id, date, event_vehicle_detected_plate_number, event_vehicle_lpn_detection_status, "stationa1", "stationa5201", "stationa13", "stationa2", "stationa23", "stationb313", "stationa4202"
, "stationa41", "stationb504" ) VALUES('{payload['event_id']}', '{payload['event_timestamp']}', '{payload['event_vehicle_detected_plate_number']}', '{payload['event_vehicle_lpn_detection_status']}', '{payload['stationa1']}', '{payload['stationa5201']}', '{payload['stationa13']}', '{payload['stationa2']}', '{payload['stationa23']}', '{payload['stationb313']}', '{payload['stationa4202']}', '{payload['stationa41']}', '{payload['stationb504']}'
)""")
                print("===============================================")
                print(payload)
                print("Message written to DB successfully")
                print("===============================================")
            except Exception as e:
                print(e)
                print("Exiting ....")
                sys.exit(1)
    except Exception as e:
        print(e.message)
        print("Exiting ....")
        sys.exit(1)
    finally:
        await kafkaConsumer.stop()
loop.run_until_complete(consume())
