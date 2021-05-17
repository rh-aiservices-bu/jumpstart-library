# Working Queries

```

select count(*) FROM  event ;

select count(*) FROM  vehicle_metadata ;

SELECT vehicle_metadata.vehicle_color, vehicle_metadata.vehicle_make, event.event_vehicle_detected_plate_number as Detected_Plate from vehicle_metadata, event WHERE vehicle_metadata.vehicle_registered_plate_number = event.event_vehicle_detected_plate_number;

SELECT vehicle_metadata.vehicle_color, vehicle_metadata.vehicle_make, event.event_vehicle_detected_plate_number as Detected_Plate, 'stationa5201' as Toll_Station_ID from vehicle_metadata, event WHERE vehicle_metadata.vehicle_registered_plate_number = event.event_vehicle_detected_plate_number AND event.stationa5201 = TRUE;






```