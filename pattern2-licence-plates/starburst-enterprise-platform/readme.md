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

helm upgrade sep-hive starburstdata/starburst-hive \
  --install \
  --version 356.0.0 \
  --values ./hms-config.yaml

oc create -f postgresql_service.yaml

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


## Connecting Presto from Superset

presto://coordinator.presto.svc.cluster.local:8080/postgresql-lpr

## Connecting presto with Object Storage

CREATE TABLE hive.s3.customer (
   custkey BIGINT,
   name VARCHAR,
   address VARCHAR
)
WITH (
   format='CSV', # <-- or parquet
external_location='s3://<bucket-name>/hive/customer')


