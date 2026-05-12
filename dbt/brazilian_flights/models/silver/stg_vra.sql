{{ config(
    materialized='table',
    catalog='workspace',
    schema='silver'
) }}

SELECT
    icao_empresa_aerea                                          AS airline_icao,
    TRY_CAST(numero_voo AS INT)                                     AS flight_number,
    icao_aerodromo_origem                                       AS origin_icao,
    icao_aerodromo_destino                                      AS destination_icao,
    TRY_TO_TIMESTAMP(partida_prevista, 'yyyy-MM-dd HH:mm:ss')  AS scheduled_departure,
    TRY_TO_TIMESTAMP(partida_real, 'yyyy-MM-dd HH:mm:ss')      AS actual_departure,
    TRY_TO_TIMESTAMP(chegada_prevista, 'yyyy-MM-dd HH:mm:ss')  AS scheduled_arrival,
    TRY_TO_TIMESTAMP(chegada_real, 'yyyy-MM-dd HH:mm:ss')      AS actual_arrival,
    situacao_voo                                                AS flight_status,
    codigo_justificativa                                        AS cancellation_code,

    -- colunas calculadas
    DATEDIFF(MINUTE,
        TRY_TO_TIMESTAMP(partida_prevista, 'yyyy-MM-dd HH:mm:ss'),
        TRY_TO_TIMESTAMP(partida_real, 'yyyy-MM-dd HH:mm:ss')
    )                                                           AS departure_delay_min,

    DATEDIFF(MINUTE,
        TRY_TO_TIMESTAMP(chegada_prevista, 'yyyy-MM-dd HH:mm:ss'),
        TRY_TO_TIMESTAMP(chegada_real, 'yyyy-MM-dd HH:mm:ss')
    )                                                           AS arrival_delay_min,

    YEAR(TRY_TO_TIMESTAMP(partida_prevista, 'yyyy-MM-dd HH:mm:ss'))  AS year,
    MONTH(TRY_TO_TIMESTAMP(partida_prevista, 'yyyy-MM-dd HH:mm:ss')) AS month

FROM {{ source('bronze', 'vra') }}
WHERE icao_empresa_aerea IS NOT NULL
  AND icao_empresa_aerea != 'ICAO Empresa Aérea'
  AND partida_prevista IS NOT NULL
