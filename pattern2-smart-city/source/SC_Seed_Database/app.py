from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
import json, urllib.request
import os, sys

JSON_DB_FILE = "vehicle_metadata_db.json"

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'dbpassword')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_NAME = os.getenv('TABLE_NAME','vehicle_metadata')

engine = create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})
Base = declarative_base()
TABLE_ID = Sequence(TABLE_NAME+'_id_seq', start=1000)

class Create_Table(Base):
    __tablename__ = TABLE_NAME
    id = Column(Integer, TABLE_ID,  primary_key=True, index=True, server_default=TABLE_ID.next_value())
    vehicle_registered_plate_number = Column(String, primary_key=True, index=True, unique=True)
    vehicle_color = Column(String)
    vehicle_make = Column(String)
    vehicle_body_type = Column(String)
    vehicle_make_model = Column(String)
    vehicle_model_year = Column(String)
    vehicle_registered_city = Column(String)
    vehicle_owner_name = Column(String)
    vehicle_owner_address = Column(String)
    vehicle_owner_city = Column(String)
    vehicle_owner_zip_code = Column(String)
    vehicle_owner_contact_number = Column(String)
    customer_id = Column(String)
    customer_balance = Column(Integer)
    customer_name = Column(String)
    customer_address = Column(String)
    customer_city = Column(String)
    customer_zip_code = Column(String)
    customer_contact_number = Column(String)
    metadata_image_name= Column(String)

## Create Table if does not exists
Create_Table.__table__.create(bind=engine, checkfirst=True)

with open(JSON_DB_FILE) as db_source:
    data = json.load(db_source)

connection = engine.connect()

for count in range(len(data)):
    try:
        connection.execute(f"""INSERT INTO public.{TABLE_NAME}(vehicle_registered_plate_number,vehicle_color,vehicle_make,vehicle_body_type,vehicle_make_model,vehicle_model_year,vehicle_registered_city,vehicle_owner_name,vehicle_owner_address,vehicle_owner_city,vehicle_owner_zip_code,vehicle_owner_contact_number,customer_id,customer_balance,customer_name,customer_address,customer_city,customer_zip_code,customer_contact_number,metadata_image_name) VALUES('{data[count]['vehicle_registered_plate_number']}', '{data[count]['vehicle_color']}', '{data[count]['vehicle_make']}', '{data[count]['vehicle_body_type']}', '{data[count]['vehicle_make_model']}', '{data[count]['vehicle_model_year']}', '{data[count]['vehicle_registered_city']}', '{data[count]['vehicle_owner_name']}', '{data[count]['vehicle_owner_address']}', '{data[count]['vehicle_owner_city']}', '{data[count]['vehicle_owner_zip_code']}', '{data[count]['vehicle_owner_contact_number']}', '{data[count]['customer_id']}', '{data[count]['customer_balance']}', '{data[count]['customer_name']}', '{data[count]['customer_address']}', '{data[count]['customer_city']}', '{data[count]['customer_zip_code']}', '{data[count]['customer_contact_number']}', '{data[count]['metadata_image_name']}')""")
    except:
        print("====================== Error inserting record to database ======================")
        print(sys.exc_info()[1])
    else:
        print(" Record added to DB successfully")