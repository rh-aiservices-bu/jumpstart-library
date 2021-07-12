# Top customers with Pollution Fee
```
select vehicle_owner_name, vehicle_registered_plate_number, vehicle_model_year, customer_pollution_fee_balance  as Pollution_Fee_Balance, vehicle_owner_address, vehicle_owner_city
FROM vehicle_metadata 
where customer_pollution_fee_balance  > 0
ORDER by customer_pollution_fee_balance DESC  
```
# Top customers with Toll Fee Balance
```
select vehicle_owner_name, vehicle_registered_plate_number, customer_toll_fee_balance as Toll_Fee_Balance, vehicle_owner_address, vehicle_owner_city
FROM vehicle_metadata
where customer_toll_fee_balance > 0
ORDER by customer_toll_fee_balance DESC
```

# ODF-PGSQL : Get vehicle by make model
```
SELECT v.vehicle_make_model AS "Vehicle Make Model"
FROM hive.odf.event AS e
LEFT JOIN "postgresql-lpr".public.vehicle_metadata AS v
ON e.event_vehicle_detected_plate_number = v.vehicle_registered_plate_number
```

# ODF-PGSDQL : Get vehicle by station id
```
SELECT e.event_timestamp,
  e.event_vehicle_detected_plate_number AS "License Plate",
  v.vehicle_make_model AS "Vehicle Make Model",
  v.vehicle_owner_name AS "Vehicle Owner",
  CASE WHEN stationa1 = true THEN 'stationa1'
       WHEN stationa13 = true THEN 'stationa13'
       WHEN stationa2 = true THEN 'stationa2'
       WHEN stationa23 = true THEN 'stationa23'
       WHEN stationb313 = true THEN 'stationb313'
       WHEN stationa4202 = true THEN 'stationa4202'
       WHEN stationb504 = true THEN 'stationb504'
       WHEN stationa41 = true THEN 'stationa41'
       WHEN stationa5201 = true THEN 'stationa5201'
       END AS station
FROM hive.odf.event AS e
LEFT JOIN "postgresql-lpr".public.vehicle_metadata AS v
ON e.event_vehicle_detected_plate_number = v.vehicle_registered_plate_number
```

# PGSQL : Get vehicle by Station ID
```
SELECT
  CASE WHEN stationa1 = true THEN 'stationa1'
       WHEN stationa13 = true THEN 'stationa13'
       WHEN stationa2 = true THEN 'stationa2'
       WHEN stationa23 = true THEN 'stationa23'
       WHEN stationb313 = true THEN 'stationb313'
       WHEN stationa4202 = true THEN 'stationa4202'
       WHEN stationb504 = true THEN 'stationb504'
       WHEN stationa41 = true THEN 'stationa41'
       WHEN stationa5201 = true THEN 'stationa5201'
       END AS station
FROM public.event AS e
LEFT JOIN public.vehicle_metadata AS v
ON e.event_vehicle_detected_plate_number = v.vehicle_registered_plate_number

```

# PGSQL : Get Vehicle by Make Model
```
SELECT v.vehicle_make_model AS "Vehicle Make Model"
FROM public.event AS e
LEFT JOIN public.vehicle_metadata AS v
ON e.event_vehicle_detected_plate_number = v.vehicle_registered_plate_number
```

# Total_Toll_Fee_Collection
```
select SUM(customer_toll_fee_balance)  as Total_Toll_Fee_Collection
FROM vehicle_metadata
where customer_toll_fee_balance  > 0
```

# Total pollution fee collection
```
select SUM(customer_pollution_fee_balance)  as Total_Pollution_Fee_Collection
FROM vehicle_metadata
where customer_pollution_fee_balance  > 0
```

# Total vehicles passed toll stations
```
select COUNT(*) from public.event ;
```
