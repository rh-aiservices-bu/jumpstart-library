import os
from string import Template
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from sqlalchemy import create_engine,MetaData
import sqlalchemy as db

# Images on local S3
service_point = os.environ['SERVICE_POINT']
bucket_name = os.environ['BUCKET_NAME']

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'HT@1202k')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_NAME = os.getenv('TABLE_NAME','event')

def get_last_image():
    """Retrieves the last uploaded image according to helper database timestamp."""
    engine = db.create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME,  pool_pre_ping=True)
    connection = engine.connect()
    metadata = db.MetaData()
    event = db.Table('event',metadata, autoload=True, autoload_with=engine)
    try:
        query = """SELECT e.event_vehicle_detected_plate_number,
                    e.date,
                    v.vehicle_make,
                    v.vehicle_color,
                    v.vehicle_body_type ,
                    v.vehicle_owner_name,
                    v.metadata_image_name
                    FROM event  AS e
                    LEFT JOIN vehicle_metadata AS v
                    ON e.event_vehicle_detected_plate_number = v.vehicle_registered_plate_number
                    ORDER by e.date DESC
                    LIMIT 1"""
        rs = connection.execute(query).fetchall()
        for row in rs:
            row_as_dict = dict(row)
            result = row_as_dict["metadata_image_name"]
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise
    connection.close()
    return result

# Response templates
LOCATION_TEMPLATE = Template("""<img src="${service_point}/${bucket_name}/images/${image_name}" style="width:300px;"></img>""")
## Application
app = FastAPI()

@app.get("/last_image", response_class=HTMLResponse)
async def last_image():
    image_name = get_last_image()
    if image_name != "":
        html = LOCATION_TEMPLATE.substitute(service_point=service_point, bucket_name=bucket_name, image_name=image_name)
    else:
        html = '<h2 style="font-family: Roboto,Helvetica Neue,Arial,sans-serif;text-align: center; color: white;font-size: 15px;font-weight: 400;">No image to show</h2>'
    return html

@app.get("/health")
def health():
    # engine = db.create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME,  pool_pre_ping=True)
    # connection = engine.connect()
    # metadata = db.MetaData()
    # event = db.Table('event',metadata, autoload=True, autoload_with=engine)
    #return {"Health_Status": "All_is_well", "engine": engine, "connection": connection, "metadata": metadata, "event" : event}
    return {"Health_Status": "All_is_well"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
    )
