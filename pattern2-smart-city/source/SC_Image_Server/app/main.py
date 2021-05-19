import os
from string import Template
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from fastapi import FastAPI

from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HT@1202k')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_NAME = os.getenv('TABLE_NAME','event')

engine = create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})

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


def get_last_image():
    """Retrieves the last uploaded image according to helper database timestamp."""

    try:
        connection = engine.connect()
        
        cursor = cnx.cursor()
        query = 'SELECT name FROM ' + bucket_table[bucket_name] + ' ORDER BY time DESC LIMIT 1;'
        cursor.execute(query)
        data = cursor.fetchone()
        if data is not None:
            result = data[0]
        else:
            result = ""
        cursor.close()
        cnx.close()

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

    return result

# Response templates 
LOCATION_TEMPLATE = Template("""
    <img src="${service_point}/${bucket_name}/${image_name}" style="width:260px;"></img>""")

## Application  

app = FastAPI()

@app.get("/last_image")
async def last_image():
    image_name = get_last_image()   
    if image_name != "":   
        html = LOCATION_TEMPLATE_BIG.substitute(service_point=service_point, bucket_name=bucket_name, image_name=image_name)
    else:
        html = '<h2 style="font-family: Roboto,Helvetica Neue,Arial,sans-serif;text-align: center; color: white;font-size: 15px;font-weight: 400;">No image to show</h2>'
    return html