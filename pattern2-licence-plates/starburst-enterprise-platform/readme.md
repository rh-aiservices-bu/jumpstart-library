- Install helm 3.x client
- oc new-project presto
```
helm repo add \
  --username redhat \
  --password JBXjLPv6Scch5t8Dk2zLnZhgS \
  starburstdata \
  https://harbor.starburstdata.net/chartrepo/starburstdata

helm repo list

helm search repo

oc create secret generic mylicense --from-file=starburstdata.license

## If using existing PGDB for HMS >> Create PGSQL DB and Users
oc projct <namespace_running_pgsql_pod>
oc rsh <pgsql_pod>
create database hive;
create user hive with encrypted password 'hive';
grant all privileges on database hive to hive;
ALTER DATABASE hive OWNER TO hive;

helm upgrade sep-hive starburstdata/starburst-hive \
  --install \
  --version 356.0.0 \
  --values ./hms-config.yaml

# Only required for internal postgresql db
oc create -f postgresql_service_only_for_internal_PGDB.yaml

helm upgrade sep-cluster starburstdata/starburst-enterprise \
  --install \
  --version 356.0.0 \
  --values ./sep-config.yaml

oc expose svc/coordinator
oc port-forward svc/coordinator 8080:8080

```
- visit http://127.0.0.1:8080

- Download trino cli

./trino --server localhost:8080 --catalog hive --schema default
Or
./trino --server localhost:8080 --catalog postgresql-lpr --schema default
```
trino:default> show catalogs;
    Catalog
----------------
 postgresql-internal
 postgresql-lpr
 s3
 system
 tpcds-testdata
 tpch
(6 rows)

```

```
trino:public> show schemas;
       Schema
--------------------
 information_schema
 pg_catalog
 public
(3 rows)
```

```
trino:pgdb> show tables from public;
      Table
------------------
 event
 vehicle_metadata
(2 rows)

Query 20210513_202303_00007_ace7y, FINISHED, 2 nodes
Splits: 19 total, 19 done (100.00%)
0.33 [2 rows, 53B] [6 rows/s, 160B/s]

trino:pgdb>
```

```
trino:pgdb> select count(*) from public.event ;
 _col0
--------
 613798
(1 row)

Query 20210513_202504_00010_ace7y, FINISHED, 1 node
Splits: 17 total, 17 done (100.00%)
0.99 [1 rows, 0B] [1 rows/s, 0B/s]
```
```
 karasing@karasing-mac  ~/temp  ./trino --server localhost:8080 --catalog postgresql-lpr --schema pgdb
trino:pgdb> show catalogs;
       Catalog
---------------------
 postgresql-internal
 postgresql-lpr
 s3
 system
 tpcds-testdata
 tpch
(6 rows)

Query 20210513_202726_00013_ace7y, FINISHED, 1 node
Splits: 19 total, 19 done (100.00%)
0.31 [0 rows, 0B] [0 rows/s, 0B/s]

trino:pgdb> show schemas;
       Schema
--------------------
 information_schema
 pg_catalog
 public
(3 rows)

Query 20210513_202731_00014_ace7y, FINISHED, 2 nodes
Splits: 19 total, 19 done (100.00%)
0.31 [3 rows, 49B] [9 rows/s, 157B/s]

trino:pgdb>
trino:pgdb> show tables from public;
      Table
------------------
 event
 vehicle_metadata
(2 rows)

Query 20210513_202740_00015_ace7y, FINISHED, 2 nodes
Splits: 19 total, 19 done (100.00%)
0.31 [2 rows, 53B] [6 rows/s, 170B/s]

trino:pgdb>
```
- more hive commands
```
./trino --server localhost:8080 --catalog postgresql-lpr --schema public
show tables;

show create table public.event;
describe event;
```


## Connecting Presto from Superset

presto://coordinator.presto.svc.cluster.local:8080/postgresql-lpr

## Connecting presto with Object Storage

- parquet tables

CREATE TABLE hive.s3.customer (
   custkey BIGINT,
   name VARCHAR,
   address VARCHAR
)
WITH (
   format='CSV', # <-- or parquet
external_location='s3://<bucket-name>/hive/customer')

- sequence file format table

CREATE EXTERNAL TABLE s3_events(a_col string, b_col bigint, c_col array<string>)
STORED AS SEQUENCEFILE
LOCATION 's3://bucketname/path/subpath/';

CREATE EXTERNAL TABLE s3_events(date timestamp, event_id string, event_vehicle_detected_plate_number string, event_vehicle_detected_lat string, event_vehicle_detected_long string, event_vehicle_lpn_detection_status string, stationa1 boolean, stationa5201 boolean, stationa13 boolean, stationa2 boolean, stationa23 boolean, stationb313 boolean, stationa4202 boolean, stationa41 boolean, stationb504 boolean) STORED AS SEQUENCEFILE LOCATION 's3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/lpr/';



CREATE SCHEMA hive.secor WITH (location = 's3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/');

```
trino:default> CREATE SCHEMA s3.hive WITH (location = 's3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/')
            -> ;
CREATE SCHEMA
trino:default>
trino:default> show schemas;
       Schema
--------------------
 default
 hive
 information_schema
(3 rows)

Query 20210521_211940_00075_ct7yn, FINISHED, 2 nodes
Splits: 19 total, 19 done (100.00%)
0.35 [3 rows, 44B] [8 rows/s, 124B/s]

trino:default>
```

CREATE TABLE IF NOT EXISTS hive.secor.event(date timestamp, event_id varchar, event_vehicle_detected_plate_number varchar, event_vehicle_detected_lat varchar, event_vehicle_detected_long varchar, event_vehicle_lpn_detection_status varchar, stationa1 boolean, stationa5201 boolean, stationa13 boolean, stationa2 boolean, stationa23 boolean, stationb313 boolean, stationa4202 boolean, stationa41 boolean, stationb504 boolean) with ( external_location = 's3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/lpr/', format = 'SEQUENCEFILE' );

```
trino:default> CREATE TABLE IF NOT EXISTS s3.hive.event(date timestamp, event_id varchar, event_vehicle_detected_plate_number varchar, event_vehicle_detected_lat varchar, event_vehicle_detected_long varchar, event_vehicle_lpn_detection_status varchar, stationa1 boolean, stationa5201 boolean, stationa13 boolean, stationa2 boolean, stationa23 boolean, stationb313 boolean, stationa4202 boolean, stationa41 boolean, stationb504 boolean) with ( external_location = 's3://secor-bucket-9af181ee-216d-483e-8fb1-cdecc2015b63/raw_logs/lpr/', format = 'SEQUENCEFILE' );
CREATE TABLE
trino:default> describe event;
Query 20210521_213633_00079_ct7yn failed: line 1:1: Table 's3.default.event' does not exist
describe event

trino:default> describe s3.hive.event;
               Column                |     Type     | Extra | Comment
-------------------------------------+--------------+-------+---------
 date                                | timestamp(3) |       |
 event_id                            | varchar      |       |
 event_vehicle_detected_plate_number | varchar      |       |
 event_vehicle_detected_lat          | varchar      |       |
 event_vehicle_detected_long         | varchar      |       |
 event_vehicle_lpn_detection_status  | varchar      |       |
 stationa1                           | boolean      |       |
 stationa5201                        | boolean      |       |
 stationa13                          | boolean      |       |
 stationa2                           | boolean      |       |
 stationa23                          | boolean      |       |
 stationb313                         | boolean      |       |
 stationa4202                        | boolean      |       |
 stationa41                          | boolean      |       |
 stationb504                         | boolean      |       |
(15 rows)

Query 20210521_213641_00080_ct7yn, FINISHED, 2 nodes
Splits: 19 total, 19 done (100.00%)
0.37 [15 rows, 1.03KB] [40 rows/s, 2.82KB/s]

trino:default>
```

trino:default> select * from s3.hive.event Limit 10;

Query 20210521_213743_00081_ct7yn, FAILED, 1 node
Splits: 17 total, 0 done (0.00%)
0.31 [0 rows, 0B] [0 rows/s, 0B/s]

Query 20210521_213743_00081_ct7yn failed: null (Service: Amazon S3; Status Code: 403; Error Code: InvalidAccessKeyId; Request ID: tx0000000000000000843e9-0060a82827-aca0bc-ocs-storagecluster-cephobjectstore; S3 Extended Request ID: aca0bc-ocs-storagecluster-cephobjectstore-ocs-storagecluster-cephobjectstore; Proxy: null)

trino:default>


{"event_timestamp": "2021-05-21T20:44:09.028536", "event_id": "296cf40701914bbb9a37f87db84afb9c", "event_vehicle_detected_plate_number": "BPT00O1", "event_vehicle_detected_lat": "51.58893", "event_vehicle_detected_long": "-0.20724", "event_vehicle_lpn_detection_status": "Successful", "stationa1": "true", "stationa5201": "false", "stationa13": "false", "stationa2": "false", "stationa23": "false", "stationb313": "false", "stationa4202": "false", "stationa41": "false", "stationb504": "false"}

```
trino:public> select * from s3.hive.event;

Query 20210522_192124_00013_r9ie5, FAILED, 1 node
Splits: 16 total, 0 done (0.00%)
0.46 [0 rows, 0B] [0 rows/s, 0B/s]

Query 20210522_192124_00013_r9ie5 failed: null (Service: Amazon S3; Status Code: 403; Error Code: InvalidAccessKeyId; Request ID: tx00000000000000008ea3e-0060a959b5-ab90b9-ocs-storagecluster-cephobjectstore; S3 Extended Request ID: ab90b9-ocs-storagecluster-cephobjectstore-ocs-storagecluster-cephobjectstore; Proxy: null)

trino:public>
```
https://pastebin.com/raw/tJ8tnrhE

##  Test using TPCDS

oc get ob obc-license-plate-recognition-secor-bucket -n license-plate-recognition -o yaml | grep -i cephUser:

oc rsh rook-toolbox
radosgw-admin user modify --uid=ceph-user-DH6eHw6z --max-buckets=100


s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)" mb s3://tiny

s3cmd --access_key=7NS6UR50MP07EH5PQZ51 --secret_key=I0v9WC0XchfxHx3tPwj0a8JiMk2zUoq99LZHMj7M --no-ssl  --host=s3.data.local --host-bucket="s3.data.local/%(bucket)" ls  s3://tiny

CREATE SCHEMA odf.tpch_tiny WITH (location = 's3a://tiny-presto/');

CREATE SCHEMA hive.tpch_tiny WITH (location = 's3://tiny/');

-  Move the customer data from the tiny generated tpch data into MinIO uing a CTAS query. Run the following query and if you like, watch it running on the Trino UI:

CREATE TABLE hive.tpch_tiny.customer  WITH (format = 'ORC', external_location = 's3://tiny/customer') AS SELECT * FROM tpch.tiny.customer;

CREATE TABLE "aws-s3".tpch_tiny.customer  WITH (format = 'ORC', external_location = 's3://tiny-presto/customer') AS SELECT * FROM tpch.tiny.customer;



CREATE TABLE odf.tpch_tiny.ted (comments VARCHAR) WITH (format='CSV', external_location='s3://tiny/ted');


TBLPROPERTIES ("transactional"="false")

SELECT * FROM s3.tiny.customer LIMIT 50;

In order for Trino to know where to locate this file, it uses the Hive metastore to manage and store this information or metadata in a relational database that the metastore points to, in this case our pgsql instance. 

SELECT DB_ID, DB_LOCATION_URI, NAME, OWNER_NAME, OWNER_TYPE, CTLG_NAME FROM metastore_db.DBS;

SELECT 
 t.TBL_ID, 
 t.DB_ID, 
 t.OWNER, 
 t.TBL_NAME, 
 t.TBL_TYPE,
 t.SD_ID
FROM metastore_db.TBLS t 
 JOIN metastore_db.DBS d 
  ON t.DB_ID= d.DB_ID 
WHERE d.NAME = 'tiny';
- You may notice the location for the table seems to be missing but that information is actually on another table. The next query will show this location. Take note of the SD_ID before running the next query.

SELECT 
 s.SD_ID,
 s.INPUT_FORMAT,
 s.LOCATION,
 s.SERDE_ID 
FROM metastore_db.TBLS t 
 JOIN metastore_db.DBS d
  ON t.DB_ID = d.DB_ID
 JOIN metastore_db.SDS s 
  ON t.SD_ID = s.SD_ID
WHERE t.TBL_NAME = 'customer'
 AND d.NAME='tiny';

- To find out the serializer used, run the following query:

SELECT 
 sd.SERDE_ID,
 sd.NAME,
 sd.SLIB
FROM metastore_db.TBLS t 
 JOIN metastore_db.DBS d
  ON t.DB_ID = d.DB_ID
 JOIN metastore_db.SDS s 
  ON t.SD_ID = s.SD_ID
 JOIN metastore_db.SERDES sd 
  ON s.SERDE_ID = sd.SERDE_ID
WHERE t.TBL_NAME = 'customer'
 AND d.NAME='tiny';

- Our last metadata query is looking at the columns on the table.

SELECT c.* 
FROM metastore_db.TBLS t
 JOIN metastore_db.DBS d
  ON t.DB_ID = d.DB_ID
 JOIN metastore_db.SDS s
  ON t.SD_ID = s.SD_ID
 JOIN metastore_db.COLUMNS_V2 c
  ON s.CD_ID = c.CD_ID
WHERE t.TBL_NAME = 'customer'
 AND d.NAME='tiny'
ORDER by CD_ID, INTEGER_IDX;


### Trying with AWS S3


CREATE SCHEMA "aws-s3".tpch_tiny WITH (location = 's3a://tiny-presto/');

CREATE TABLE "aws-s3".tpch_tiny.customer  WITH (format = 'ORC', external_location = 's3://tiny-presto/customer') AS SELECT * FROM tpch.tiny.customer;

https://pastebin.com/raw/YzaRPeve


CREATE TABLE odf.tpch_tiny.customer ( custkey BIGINT, name VARCHAR, address VARCHAR ) WITH (
   format='CSV', # <-- or parquet
external_location='s3://<bucket-name>/hive/customer')


hive.create-empty-bucket-files=true


SET SESSION hive.create-empty-bucket-files=true;

CREATE SCHEMA hive.web WITH (location = 's3://tiny/');

CREATE TABLE odf.web.page_views ( view_time timestamp, user_id bigint, page_url varchar, ds date, country varchar) WITH (
  format = 'ORC',
  partitioned_by = ARRAY['ds', 'country'],
  bucketed_by = ARRAY['user_id'],
  bucket_count = 50
);



