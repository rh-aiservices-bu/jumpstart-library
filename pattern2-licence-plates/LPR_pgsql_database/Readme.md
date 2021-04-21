## Installing PGSQL
```
export PGO_OPERATOR_NAMESPACE=pgdb
oc create project "$PGO_OPERATOR_NAMESPACE"

oc patch storageclass ocs-storagecluster-cephfs -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}'

oc patch storageclass thin -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "false"}}}'

For the PostgreSQL Operator and PostgreSQL clusters to run in the recommended restricted Security Context Constraint, edit conf/postgres-operator/pgo.yaml and set DisableFSGroup to true.
oc -n pgo scale --replicas 0 deployment/postgres-operator
oc -n pgo scale --replicas 1 deployment/postgres-operator



# this variable is the name of the cluster being created
export pgo_cluster_name=pgdb
# this variable is the namespace the cluster is being deployed into
export cluster_namespace=pgdb
# this variable is set to the location of your image repository
export cluster_image_prefix=registry.developers.crunchydata.com/crunchydata

cat <<-EOF > "${pgo_cluster_name}-pgcluster.yaml"
apiVersion: crunchydata.com/v1
kind: Pgcluster
metadata:
  annotations:
    current-primary: ${pgo_cluster_name}
  labels:
    crunchy-pgha-scope: ${pgo_cluster_name}
    deployment-name: ${pgo_cluster_name}
    name: ${pgo_cluster_name}
    pg-cluster: ${pgo_cluster_name}
    pgo-version: 4.6.2
    pgouser: admin
  name: ${pgo_cluster_name}
  namespace: ${cluster_namespace}
spec:
  BackrestStorage:
    accessmode: ReadWriteMany
    matchLabels: ""
    name: ""
    size: 1G
    storageclass: ""
    storagetype: create
    supplementalgroups: ""
  PrimaryStorage:
    accessmode: ReadWriteMany
    matchLabels: ""
    name: ${pgo_cluster_name}
    size: 1G
    storageclass: ""
    storagetype: create
    supplementalgroups: ""
  ReplicaStorage:
    accessmode: ReadWriteMany
    matchLabels: ""
    name: ""
    size: 1G
    storageclass: ""
    storagetype: create
    supplementalgroups: ""
  annotations: {}
  ccpimage: crunchy-postgres-ha
  ccpimageprefix: ${cluster_image_prefix}
  ccpimagetag: centos8-13.2-4.6.2
  clustername: ${pgo_cluster_name}
  database: ${pgo_cluster_name}
  exporterport: "9187"
  limits: {}
  name: ${pgo_cluster_name}
  namespace: ${cluster_namespace}
  pgDataSource:
    restoreFrom: ""
    restoreOpts: ""
  pgbadgerport: "10000"
  pgoimageprefix: ${cluster_image_prefix}
  podAntiAffinity:
    default: preferred
    pgBackRest: preferred
    pgBouncer: preferred
  port: "5432"
  tolerations: []
  user: hippo
  userlabels:
    pgo-version: 4.6.2
EOF

oc apply -f "${pgo_cluster_name}-pgcluster.yaml"


# namespace that the cluster is running in
export PGO_OPERATOR_NAMESPACE=pgdb
# name of the cluster
export pgo_cluster_name=hippo
# name of the user whose password we want to get
export pgo_cluster_username=hippo

# get the password of the user and set it to a recognized psql environmental variable
export PGPASSWORD=$(oc -n "${PGO_OPERATOR_NAMESPACE}" get secrets \
  "${pgo_cluster_name}-${pgo_cluster_username}-secret" -o "jsonpath={.data['password']}" | base64 -d)

# set up a port-forward either in a new terminal, or in the same terminal in the background:
oc -n pgo port-forward svc/hippo 5432:5432 &

psql -h localhost -U "${pgo_cluster_username}" "${pgo_cluster_name}"


```
- Using Openshift template

```
oc new-app --name postgresql-db --template=postgresql-persistent -p 
POSTGRESQL_USER=dbadmin -p POSTGRESQL_PASSWORD=HT@1202k -p POSTGRESQL_DATABASE=pgdb

#oc expose svc/postgresql --port='5432'

oc port-forward postgresql-1-d6h9t 5432:5432

oc rsh postgresql-1-d6h9t
psql pgdb dbadmin


CREATE TABLE products (
    product_no integer,
    name text,
    price numeric
);
\d
INSERT INTO products VALUES (1, 'Cheese', 9.99);
INSERT INTO products VALUES (1, 'Milk', 2.99);
INSERT INTO products VALUES (1, 'Tomato', 3.99);
 \d products
select * from public.products;

```

```
psql -h 127.0.0.1 -p 5432 -U dbadmin -w HT@1202k -d pgdb
\d
select * from public.products;
```

```
 oc delete all -l app=postgresql-db
 oc delete pvc postgresql
 oc delete secret postgresql
```

```
CREATE TABLE vehicle_metadata (
id SERIAL,
vehicle_registered_plate_number VARCHAR NOT NULL PRIMARY KEY,
vehicle_color VARCHAR NOT NULL,
vehicle_make VARCHAR NOT NULL,
vehicle_body_type VARCHAR NOT NULL,
vehicle_make_model VARCHAR NOT NULL,
vehicle_model_year VARCHAR NOT NULL,
vehicle_registered_city VARCHAR NOT NULL,
vehicle_owner_name VARCHAR NOT NULL,
vehicle_owner_address VARCHAR NOT NULL,
vehicle_owner_city VARCHAR NOT NULL,
vehicle_owner_zip_code VARCHAR NOT NULL,
vehicle_owner_contact_number VARCHAR NOT NULL,
customer_id VARCHAR NOT NULL,
customer_balance VARCHAR NOT NULL,
customer_name VARCHAR NOT NULL,
customer_address VARCHAR NOT NULL,
customer_city VARCHAR NOT NULL,
customer_zip_code VARCHAR NOT NULL,
customer_contact_number VARCHAR NOT NULL
);

CREATE TABLE events_data (
id SERIAL,
event_timestamp VARCHAR NOT NULL,
event_id INT NOT NULL,
event_vehicle_detected_plate_number VARCHAR NOT NULL,
event_vehicle_detected_lat VARCHAR NOT NULL,
event_vehicle_detected_long VARCHAR NOT NULL,
event_vehicle_lpn_detection_status VARCHAR NOT NULL
);

```