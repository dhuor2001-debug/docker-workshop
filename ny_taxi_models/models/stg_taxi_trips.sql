{{ config(materialized='table') }}

SELECT
    tpep_pickup_datetime AS pickup_datetime,
    tpep_dropoff_datetime AS dropoff_datetime,
    passenger_count,
    trip_distance,
    "PULocationID" AS pickup_location_id,
    "DOLocationID" AS dropoff_location_id,
    fare_amount,
    tip_amount,
    total_amount
FROM public.yellow_taxi_trips_automated
WHERE passenger_count > 0 
  AND trip_distance > 0.0