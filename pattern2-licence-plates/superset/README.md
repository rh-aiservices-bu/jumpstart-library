# Working Queries

- Ideas for queries

1)  In last 1 week , get the number of vehicles that incurred dirty fee. Plot the chart with 
- x-axis : Time (Date) 
- y-axis: vehicle count

2) Total toll tax collected per day (in last 1 month). Plot the chart with 
- x-axis : Date (day of month)
- y-axis : Amount



```
select count(*) FROM  event ;

select count(*) FROM  vehicle_metadata ;

SELECT vehicle_metadata.vehicle_color, vehicle_metadata.vehicle_make, event.event_vehicle_detected_plate_number as Detected_Plate from vehicle_metadata, event WHERE vehicle_metadata.vehicle_registered_plate_number = event.event_vehicle_detected_plate_number;

SELECT vehicle_metadata.vehicle_color, vehicle_metadata.vehicle_make, event.event_vehicle_detected_plate_number as Detected_Plate, 'stationa5201' as Toll_Station_ID from vehicle_metadata, event WHERE vehicle_metadata.vehicle_registered_plate_number = event.event_vehicle_detected_plate_number AND event.stationa5201 = TRUE;

```

- Verify whats the version of super set running 
on image: 'quay.io/aiops/superset:v0.30'

Successfully pulled image "quay.io/aiops/superset:v0.30" in 6.958594017s
