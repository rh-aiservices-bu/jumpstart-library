import trino
from sqlalchemy import create_engine,MetaData
#from sqlalchemy.dialects import postgresql
import sqlalchemy as db
import os
from datetime import datetime, timedelta

def toll_and_pollution_fee_calculation(vehicle_metadata , event_result, connection, fee_type):
    '''
    For every detected license plate of vehicle entered into the city between NOW and last BATCH_TIME_MINS Minutes
    match the license plate with vehichle_metadata, if mathc found, then lookup vehicle's model year.
    If vehicle_model < 2014 , apply additional pollution fee & toll fee
    Else If vehicle_model >= 2014 , apply only toll fee
    '''
    for row in event_result:
        row_as_dict = dict(row)
        column, value = list(row_as_dict.items())[0]
        search = "%{}%".format(value)
        #print(search)

        #vehicle_metadata_query = db.select([vehicle_metadata.columns.vehicle_model_year,vehicle_metadata.columns.vehicle_registered_plate_number,vehicle_metadata.columns.customer_toll_fee_balance,vehicle_metadata.columns.customer_pollution_fee_balance]).filter(vehicle_metadata.columns.vehicle_registered_plate_number.like(search), vehicle_metadata.columns.vehicle_model_year.like('%2014%'))
        if fee_type == "toll_and_pollution":
            vehicle_metadata_query = db.select([vehicle_metadata.columns.vehicle_model_year,vehicle_metadata.columns.vehicle_registered_plate_number,vehicle_metadata.columns.customer_toll_fee_balance,vehicle_metadata.columns.customer_pollution_fee_balance]).filter(vehicle_metadata.columns.vehicle_registered_plate_number.like(search), vehicle_metadata.columns.vehicle_model_year < 2014)

        if fee_type == "toll_only":
            vehicle_metadata_query = db.select([vehicle_metadata.columns.vehicle_model_year,vehicle_metadata.columns.vehicle_registered_plate_number,vehicle_metadata.columns.customer_toll_fee_balance,vehicle_metadata.columns.customer_pollution_fee_balance]).filter(vehicle_metadata.columns.vehicle_registered_plate_number.like(search), vehicle_metadata.columns.vehicle_model_year >= 2014)

        ## Uncomment : To view the RAW SQL Statement
        #print(vehicle_metadata_query.compile(dialect=postgresql.dialect()))
        vehicle_metadata_result = connection.execute(vehicle_metadata_query).fetchall()

        if len(vehicle_metadata_result) > 0:
            for row_vehicle_metadata_result in vehicle_metadata_result:
                value_customer_toll_fee_balance = 0
                value_customer_pollution_fee_balance = 0
                row_as_dict_vehicle_metadata_result = dict(row_vehicle_metadata_result)
                print("-------------------------------------------------------------------")
                print("Applying fee for vehicle: "+ str(row_as_dict_vehicle_metadata_result))
                column_vehicle_registered_plate_number, value_vehicle_registered_plate_number = list(row_as_dict_vehicle_metadata_result.items())[1]
                column_customer_toll_fee_balance, value_customer_toll_fee_balance = list(row_as_dict_vehicle_metadata_result.items())[2]
                column_customer_pollution_fee_balance, value_customer_pollution_fee_balance= list(row_as_dict_vehicle_metadata_result.items())[2]

                value_customer_toll_fee_balance = value_customer_toll_fee_balance + int(TOLL_FEE)
                value_customer_pollution_fee_balance = value_customer_pollution_fee_balance + int(POLLUTION_FEE)

                if fee_type == "toll_and_pollution":
                    update_statement = db.update(vehicle_metadata).values(customer_toll_fee_balance=value_customer_toll_fee_balance,customer_pollution_fee_balance= value_customer_pollution_fee_balance).where(vehicle_metadata.columns.vehicle_registered_plate_number == value_vehicle_registered_plate_number )
                    print("Pollution fee applied: "+str(POLLUTION_FEE)+" £")
                    print("Total Pollution fee balance: "+str(value_customer_pollution_fee_balance)+" £")
                    ## Uncomment if record updates to be done by Trino
                    #trino_query = "UPDATE vehicle_metadata SET customer_toll_fee_balance="+str(value_customer_toll_fee_balance)+",customer_pollution_fee_balance="+str(value_customer_pollution_fee_balance)+" WHERE vehicle_metadata.vehicle_registered_plate_number="+str(value_vehicle_registered_plate_number)

                if fee_type == "toll_only":
                    update_statement = db.update(vehicle_metadata).values(customer_toll_fee_balance=value_customer_toll_fee_balance).where(vehicle_metadata.columns.vehicle_registered_plate_number == value_vehicle_registered_plate_number )

                    ## Uncomment if record updates to be done by Trino
                    #trino_query = "UPDATE vehicle_metadata SET customer_toll_fee_balance="+str(value_customer_toll_fee_balance)+" WHERE vehicle_metadata.vehicle_registered_plate_number="+str(value_vehicle_registered_plate_number)

                vehicle_metadata_result = connection.execute(update_statement)
                ## Uncomment if record updates to be done by Trino
                #trino_execute_query(trino_query)
                print("Toll fee applied: "+str(TOLL_FEE)+" £")
                print("Total Toll fee balance: "+str(value_customer_toll_fee_balance)+" £")
                print("-------------------------------------------------------------------")

## Important Note : Trino PostgreSQL connector does not support updates, hence we could not use this in this demo, instead we are using sqlalchemy ORM
## This section is here just for learning purposes
def trino_execute_query(trino_query):
    conn = trino.dbapi.connect(
        host=TRINO_ENDPOINT,
        port=TRINO_PORT,
        user=TRINO_USER,
        catalog=TRINO_CATALOG,
        schema=TRINO_SCHEMA,
    )
    cur = conn.cursor()
    print(trino_query)
    #cur.execute('SELECT COUNT(*) FROM vehicle_metadata')
    cur.execute(trino_query)
    rows = cur.fetchall()
    print(rows)

def main():
    ## Database connection string
    engine = db.create_engine('postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME, connect_args={})
    connection = engine.connect()
    metadata = db.MetaData()

    ## For event Table
    event = db.Table('event',metadata, autoload=True, autoload_with=engine)
    #print(event.columns.keys())
    #event_query = db.select([event.columns.date, event.columns.event_vehicle_detected_plate_number]).limit(5)

    ## For vehicle_metadata Table
    vehicle_metadata = db.Table('vehicle_metadata',metadata, autoload=True, autoload_with=engine)
    #print(vehicle_metadata.columns.keys())
    #vehicle_metadata_query = db.select([vehicle_metadata.columns.customer_toll_fee_balance, vehicle_metadata.columns.customer_pollution_fee_balance, vehicle_metadata.columns.vehicle_registered_plate_number]).limit(5)

    ## BATCH_TIME_MINS defines the time interval in minutes to run the batch job
    current_time_utc = datetime.utcnow()
    time_filter = current_time_utc - timedelta(minutes = int(BATCH_TIME_MINS))
    print("==========  Running batch query between "+str(current_time_utc)+ " and "+str(time_filter)+ " ==========")

    ## DB Query to find vehicles entered into city between NOW and last BATCH_TIME_MINS Minutes
    event_query = db.select([event.columns.event_vehicle_detected_plate_number]).filter(event.columns.date > time_filter)
    event_result = connection.execute(event_query).fetchall()

    toll_and_pollution_fee_calculation(vehicle_metadata , event_result, connection, fee_type="toll_and_pollution")
    toll_and_pollution_fee_calculation(vehicle_metadata , event_result, connection, fee_type="toll_only")

if __name__ == "__main__":

    TOLL_FEE = os.getenv('TOLL_FEE', 5)
    POLLUTION_FEE = os.getenv('POLLUTION_FEE', 5)
    BATCH_TIME_MINS = os.getenv('BATCH_TIME_MINS', 5)

    DB_USER = os.getenv('DB_USER', 'dbadmin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'dbpassword')
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_NAME = os.getenv('DB_NAME','pgdb')
    TABLE_EVENT = os.getenv('TABLE_EVENT','event')
    TABLE_VEHICLE_METADATA = os.getenv('TABLE_VEHICLE_METADATA','vehicle_metadata')
    ## Trino connection details
    TRINO_ENDPOINT = os.getenv('TRINO_ENDPOINT', '127.0.0.1')
    TRINO_PORT = os.getenv('TRINO_PORT', '8080')
    TRINO_USER = os.getenv('TRINO_USER', 'admin')
    TRINO_CATALOG = os.getenv('TRINO_CATALOG', 'postgresql-lpr')
    TRINO_SCHEMA = os.getenv('TRINO_SCMEMA', 'public')
    main()
