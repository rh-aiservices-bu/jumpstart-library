#import trino
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, table, column, select, MetaData, insert
import sqlalchemy as db
import os, sys
from datetime import datetime, timedelta

TOLL_FEE = os.getenv('TOLL_FEE', 5)
POLLUTION_FEE = os.getenv('POLLUTION_FEE', 5)
BATCH_TIME_MINS = os.getenv('BATCH_TIME_MINS', 5)

## Database details and connection
DB_USER = os.getenv('DB_USER', 'dbadmin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'dbpassword')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME','pgdb')
TABLE_EVENT = os.getenv('TABLE_EVENT','event')
TABLE_VEHICLE_METADATA = os.getenv('TABLE_VEHICLE_METADATA','vehicle_metadata')

engine = db.create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})
connection = engine.connect()
metadata = db.MetaData()

## Trino connection details
#conn = trino.dbapi.connect(
    # host='localhost',
    # port=8080,
    # user='admin',
    # catalog='postgresql-lpr',
    # schema='public',
#)
#cur = conn.cursor()
#cur.execute('SELECT COUNT(*) FROM vehicle_metadata')
#cur.execute('SELECT * from vehicle_metadata')
#rows = cur.fetchall()
#print(rows)

event = db.Table('event',metadata, autoload=True, autoload_with=engine)
#print(event.columns.keys())
#event_query = db.select([event.columns.date, event.columns.event_vehicle_detected_plate_number]).limit(5)

vehicle_metadata = db.Table('vehicle_metadata',metadata, autoload=True, autoload_with=engine)
#print(vehicle_metadata.columns.keys())
#vehicle_metadata_query = db.select([vehicle_metadata.columns.customer_toll_fee_balance, vehicle_metadata.columns.customer_pollution_fee_balance, vehicle_metadata.columns.vehicle_registered_plate_number]).limit(5)


## BATCH_TIME_MINS defines the time interval in minutes to run the batch job
current_time_utc = datetime.utcnow()
time_filter = current_time_utc - timedelta(minutes = BATCH_TIME_MINS)
print("==========  Running batch query between "+str(current_time_utc)+ " and "+str(time_filter)+ " ==========")


## DB Query to find vehicles entered into city between NOW and last BATCH_TIME_MINS Minutes
event_query = db.select([event.columns.event_vehicle_detected_plate_number]).filter(event.columns.date > time_filter)
event_result = connection.execute(event_query).fetchall()

'''
For every detected license plate of vehicle entered into the city between NOW and last BATCH_TIME_MINS Minutes
match the license plate with vehichle_metadata, if mathc found, then lookup vehicle's model year.
If vehicle_model < 2015 , apply additional pollution fee & toll fee
'''

for row in event_result:
    row_as_dict = dict(row)
    column, value = list(row_as_dict.items())[0]
    search = "%{}%".format(value)
    #print(search)
    
    vehicle_metadata_query = db.select([vehicle_metadata.columns.vehicle_model_year,vehicle_metadata.columns.vehicle_registered_plate_number,vehicle_metadata.columns.customer_toll_fee_balance,vehicle_metadata.columns.customer_pollution_fee_balance]).filter(vehicle_metadata.columns.vehicle_registered_plate_number.like(search), vehicle_metadata.columns.vehicle_model_year.like('%2014%'))
    vehicle_metadata_result = connection.execute(vehicle_metadata_query).fetchall()
    if len(vehicle_metadata_result) > 0:
        for row_vehicle_metadata_result in vehicle_metadata_result:
            value_customer_toll_fee_balance = 0
            value_customer_pollution_fee_balance = 0
            row_as_dict_vehicle_metadata_result = dict(row_vehicle_metadata_result)
            print("-------------------------------------------------------------------")
            print("Old  vehicle detected: "+ str(row_as_dict_vehicle_metadata_result))
            column_vehicle_registered_plate_number, value_vehicle_registered_plate_number = list(row_as_dict_vehicle_metadata_result.items())[1]
            column_customer_toll_fee_balance, value_customer_toll_fee_balance = list(row_as_dict_vehicle_metadata_result.items())[2]
            column_customer_pollution_fee_balance, value_customer_pollution_fee_balance= list(row_as_dict_vehicle_metadata_result.items())[2]
            #print(value_vehicle_registered_plate_number)
            value_customer_toll_fee_balance = value_customer_toll_fee_balance + TOLL_FEE
            value_customer_pollution_fee_balance = value_customer_pollution_fee_balance + POLLUTION_FEE
            update_statement = db.update(vehicle_metadata).values(customer_toll_fee_balance=value_customer_toll_fee_balance,customer_pollution_fee_balance= value_customer_pollution_fee_balance).where(vehicle_metadata.columns.vehicle_registered_plate_number == value_vehicle_registered_plate_number )
            vehicle_metadata_result = connection.execute(update_statement)
            print("Toll fee applied: "+str(value_customer_toll_fee_balance)+" £")
            print("Pollution fee applied: "+str(value_customer_pollution_fee_balance)+" £")
            print("-------------------------------------------------------------------")



