- Connect to trino

```
 ./trino --server localhost:8080 --catalog hive --schema default`
```

```
show catalogs;

show schemas;

CREATE SCHEMA hive.odf WITH (location = 's3://secor-bb120bd3-830f-4f62-a4a5-c2871572c826/');

CREATE TABLE IF NOT EXISTS hive.odf.event(event_timestamp timestamp, event_id varchar, event_vehicle_detected_plate_number varchar, event_vehicle_detected_lat varchar, event_vehicle_detected_long varchar, event_vehicle_lpn_detection_status varchar, stationa1 boolean, stationa5201 boolean, stationa13 boolean, stationa2 boolean, stationa23 boolean, stationb313 boolean, stationa4202 boolean, stationa41 boolean, stationb504 boolean, dt varchar) with ( external_location = 's3://secor-bb120bd3-830f-4f62-a4a5-c2871572c826/raw_logs/lpr/', format = 'ORC', partitioned_by=ARRAY['dt']);

 describe hive.odf.event;

CALL system.sync_partition_metadata(schema_name=>'odf', table_name=>'event', mode=>'FULL');
select * from hive.odf.event;

```

```
 s3cmd --access_key=MK2RT98OKJN6WEH1R0PN --secret_key=OYWYuogkGN7T0MFEwOUSxGyDjR8qLJO6YX99Lh0j --no-ssl  --host=rook-ceph-rgw-ocs-storagecluster-cephobjectstore.ope
nshift-storage.svc.cluster.local --host-bucket="rook-ceph-rgw-ocs-storagecluster-cephobjectstore.openshift-storage.svc.cluster.local/%(bucket)" ls s3://secor-bb120bd3-830
f-4f62-a4a5-c2871572c826/raw_logs/lpr/
```
