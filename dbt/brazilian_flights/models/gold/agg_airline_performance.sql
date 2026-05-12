{{ config(
    materialized='table'
) }}

SELECT
    airline_icao,
    year,
    month,
    COUNT(*)                                                    AS total_flights,
    SUM(CASE WHEN flight_status = 'REALIZADO' THEN 1 ELSE 0 END) AS completed_flights,
    SUM(CASE WHEN flight_status = 'CANCELADO' THEN 1 ELSE 0 END) AS cancelled_flights,
    ROUND(
        SUM(CASE WHEN flight_status = 'CANCELADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    )                                                           AS cancellation_rate_pct,
    ROUND(AVG(CASE WHEN departure_delay_min > 0 THEN departure_delay_min END), 1) AS avg_departure_delay_min,
    ROUND(AVG(CASE WHEN arrival_delay_min > 0 THEN arrival_delay_min END), 1)     AS avg_arrival_delay_min,
    SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END)  AS flights_delayed_gt15min,
    ROUND(
        SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    )                                                           AS delay_rate_pct

FROM {{ ref('stg_vra') }}
WHERE year IS NOT NULL
GROUP BY airline_icao, year, month
ORDER BY year, month, total_flights DESC