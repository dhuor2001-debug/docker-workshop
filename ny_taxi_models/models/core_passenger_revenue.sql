{{ config(materialized='table') }}

SELECT
    passenger_count,
    COUNT(*) as total_trips,
    ROUND(AVG(tip_amount), 2) as avg_tip_amount,
    ROUND(SUM(total_amount), 2) as total_revenue
FROM {{ ref('stg_taxi_trips') }}
GROUP BY passenger_count
ORDER BY passenger_count