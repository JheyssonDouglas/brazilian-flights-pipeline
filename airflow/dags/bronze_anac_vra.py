from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import base64
import os

ANAC_BASE_URL = "https://sistemas.anac.gov.br/dadosabertos/Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/Voo%20Regular%20Ativo%20%28VRA%29"
ANOS = [2022, 2023, 2024, 2025, 2026]
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")


def listar_meses(ano: int) -> list:
    url = f"{ANAC_BASE_URL}/{ano}/"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    meses = []
    for line in response.text.split("\n"):
        if 'href="' in line and line.strip().startswith("<a href="):
            href = line.split('href="')[1].split('"')[0]
            if href == "../":
                continue
            numero = href.split("%20")[0]
            if numero.isdigit():
                meses.append((numero.zfill(2), href))
    return sorted(meses)


def baixar_e_upload(ano: int, mes: str, href: str):
    url_mes = f"{ANAC_BASE_URL}/{ano}/{href}"
    response = requests.get(url_mes, timeout=30)
    response.raise_for_status()

    arquivo_csv = None
    for line in response.text.split("\n"):
        if 'href="' in line and ".csv" in line.lower():
            arquivo_csv = line.split('href="')[1].split('"')[0]
            break

    if not arquivo_csv:
        print(f"Nenhum CSV encontrado para {ano}/{mes}")
        return

    url_csv = f"{ANAC_BASE_URL}/{ano}/{href}{arquivo_csv}"
    print(f"Baixando: {url_csv}")

    csv_response = requests.get(url_csv, timeout=120)
    csv_response.raise_for_status()

    files_path = f"/Volumes/workspace/bronze/anac_raw/vra/{ano}/{mes}/dados.csv"
    headers = {"Authorization": f"Bearer {DATABRICKS_TOKEN}"}

    chunk_size = 512 * 1024  # 512KB por chunk
    conteudo = csv_response.content
    total_chunks = (len(conteudo) + chunk_size - 1) // chunk_size

    session = requests.Session()
    session.headers.update(headers)

    for i in range(0, len(conteudo), chunk_size):
        chunk = conteudo[i:i + chunk_size]
        chunk_num = i // chunk_size + 1

        params = {}
        if i == 0:
            params["overwrite"] = "true"

        upload_response = session.put(
            f"{DATABRICKS_HOST}/api/2.0/fs/files{files_path}",
            data=chunk,
            params=params,
            timeout=60,
        )
        upload_response.raise_for_status()
        print(f"Chunk {chunk_num}/{total_chunks} enviado — {ano}/{mes}")

    print(f"Upload concluído: {files_path}")


def ingerir_ano(ano: int, **context):
    meses = listar_meses(ano)
    print(f"Meses encontrados para {ano}: {meses}")
    for numero, href in meses:
        baixar_e_upload(ano, numero, href)


with DAG(
    dag_id="bronze_anac_vra",
    start_date=datetime(2024, 1, 1),
    schedule="0 6 1 * *",
    catchup=False,
    tags=["bronze", "anac", "vra"],
) as dag:

    for ano in ANOS:
        PythonOperator(
            task_id=f"ingerir_{ano}",
            python_callable=ingerir_ano,
            op_kwargs={"ano": ano},
        )