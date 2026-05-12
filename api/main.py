from fastapi import FastAPI, Query
from databricks import sql
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(
    title="Brazilian Flights API",
    description="API para dados de voos regulares brasileiros (ANAC)",
    version="1.0.0"
)

def get_connection():
    host = os.getenv("DATABRICKS_HOST", "").replace("https://", "").replace("http://", "")
    return sql.connect(
        server_hostname=host,
        http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    )

@app.get("/")
def root():
    return {"message": "Brazilian Flights API", "status": "ok"}

@app.get("/airlines")
def get_airlines():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT airline_icao
                FROM workspace.gold.agg_airline_performance
                ORDER BY airline_icao
            """)
            rows = cursor.fetchall()
    return {"airlines": [row[0] for row in rows]}

@app.get("/performance")
def get_performance(
    airline: str = Query(None, description="Filtrar por companhia aérea (ex: GLO, AZU, TAM)"),
    year: int = Query(None, description="Filtrar por ano (ex: 2022, 2023, 2024)")
):
    filters = ["1=1"]
    if airline:
        filters.append(f"airline_icao = '{airline.upper()}'")
    if year:
        filters.append(f"year = {year}")

    where = " AND ".join(filters)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    airline_icao,
                    year,
                    month,
                    total_flights,
                    completed_flights,
                    cancelled_flights,
                    cancellation_rate_pct,
                    avg_departure_delay_min,
                    avg_arrival_delay_min,
                    flights_delayed_gt15min,
                    delay_rate_pct
                FROM workspace.gold.agg_airline_performance
                WHERE {where}
                ORDER BY year, month
            """)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

    return {"data": [dict(zip(columns, row)) for row in rows]}

@app.get("/performance/summary")
def get_summary(year: int = Query(None, description="Filtrar por ano")):
    filter = f"WHERE year = {year}" if year else ""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    airline_icao,
                    SUM(total_flights) as total_flights,
                    ROUND(AVG(cancellation_rate_pct), 2) as avg_cancellation_rate,
                    ROUND(AVG(avg_departure_delay_min), 1) as avg_departure_delay,
                    ROUND(AVG(delay_rate_pct), 2) as avg_delay_rate
                FROM workspace.gold.agg_airline_performance
                {filter}
                GROUP BY airline_icao
                ORDER BY total_flights DESC
            """)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

    return {"data": [dict(zip(columns, row)) for row in rows]}