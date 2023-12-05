import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import pymysql
import sqlalchemy
from dotenv import load_dotenv
from flask import Flask, Request, Response, request
from google.api_core import exceptions
from google.cloud import logging, pubsub_v1, storage
from google.cloud.sql.connector import Connector

load_dotenv()

connector = Connector()
app = Flask(__name__)

INSTANCE_NAME = os.environ["INSTANCE_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]


def get_connection() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        INSTANCE_NAME,
        "pymysql",
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
    )
    return conn


pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=get_connection,
)


def make_logging_client():
    client = logging.Client()
    log_name = "requester_countries_logs"
    client.setup_logging()
    logger = client.logger(log_name)
    return logger


def make_storage_client() -> storage.Client:
    client = storage.Client()
    return client


def get_files_from_bucket(
    bucket_name: str,
    folder_name: str,
    file_name: str,
) -> Optional[str]:
    try:
        client = make_storage_client()
        prefix: str = f"{folder_name}/{file_name}"
        bucket = client.get_bucket(bucket_name)
        blob = bucket.get_blob(prefix)
        if blob is None:
            err_msg: str = "Error file not found"
            return Response(err_msg, status=404, mimetype="text/plain")

        # blobs = client.list_blobs(bucket_name, prefix=prefix)
        # print("Prefix", prefix, "blobs", blobs)
        # for blob in blobs:
        #     print(f"blob name: {blob.name}")
        # logger.log_text(
        #     f"Accessing blob: {blob.name}, and retuning the data to the user {blob.download_as_string()}"
        # )
        if blob.exists():
            blob_data = blob.download_as_string()
            return blob_data, 200, {"Content-Type": "text/html"}
        return Response(blob.download_as_string(), mimetype="text/html")
    except:
        err_msg: str = "Error file not found"
        # logger.log_text(f"Error file not found: {err_msg}, Status: 404")
        return Response(err_msg, status=404, mimetype="text/plain")


def get_bucket_path_fname(request_args: dict) -> Optional[str]:
    # "name = bucketname + '/webdir/' + str(idx) + '.html'"
    name = request_args.url
    if name is None:
        return None
    return name.split("/")[-3:]


# North Korea, Iran, Cuba, Myanmar, Iraq, Libya, Sudan, Zimbabwe and Syria
LIST_OF_ENEMY_COUNTRIES: list[str] = [
    "North Korea",
    "Iran",
    "Cuba",
    "Myanmar",
    "Iraq",
    "Libya",
    "Sudan",
    "Zimbabwe",
    "Syria",
]


def check_if_country_is_enemy(
    country: str,
) -> bool:
    return country in LIST_OF_ENEMY_COUNTRIES


@app.route(
    "/<bucket_name>/<dir>/<file>",
    methods=[
        "GET",
        "POST",
        "HEAD",
        "CONNECT",
        "OPTIONS",
        "TRACE",
        "PATCH",
        "PUT",
        "DELETE",
    ],
)
def receive_http_request(bucket_name, dir, file) -> Optional[Response]:
    # logger = make_logging_client()
    try:
        if request.method == "GET":
            if request.headers.get("X-country") is not None:
                country = request.headers.get("X-country")

                make_database_and_publish_data(
                    country=country,
                    gender=request.headers.get("X-gender"),
                    age=request.headers.get("X-age"),
                    income=request.headers.get("X-income"),
                    is_banned=request.headers.get("X-is-banned"),
                    client_ip=request.headers.get("X-client-IP"),
                    time_of_request=request.headers.get("X-time"),
                )

                if check_if_country_is_enemy(country):
                    err_msg = "Error, country is enemy"
                    make_second_database_and_publish_data(
                        request_time=request.headers.get("X-time"),
                        requested_file=file,
                        error_code=400,
                    )
                    return Response(err_msg, status=400, mimetype="text/plain")

                make_second_database_and_publish_data(
                    request_time=request.headers.get("X-time"),
                    requested_file=file,
                    error_code=200,
                )
            print(bucket_name, dir, file)
            return get_files_from_bucket(bucket_name, dir, file)
        elif request.method != "GET":
            err_msg = "Error, wrong HTTP Request Type"
            make_second_database_and_publish_data(
                request_time=request.headers.get("X-time"),
                requested_file=file,
                error_code=501,
            )
            return Response(err_msg, status=501, mimetype="text/plain")
    except exceptions.NotFound:
        err_msg = "Error, wrong HTTP Request Type"
        return Response(err_msg, status=501, mimetype="text/plain")


def create_db():
    try:
        with pool.connect() as conn:
            conn.execute(
                sqlalchemy.text(
                    """
                    CREATE TABLE IF NOT EXISTS request (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        country VARCHAR(255),
                        gender ENUM('Male', 'Female'),
                        age ENUM('0-16', '17-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+'),
                        income ENUM('0-10k', '10k-20k', '20k-40k', '40k-60k', '60k-100k', '100k-150k', '150k-250k', '250k+'),
                        is_banned BOOLEAN,
                        client_ip VARCHAR(255),
                        time_of_request TIMESTAMP)
                    """
                )
            )
            conn.execute(
                sqlalchemy.text(
                    """
                CREATE TABLE IF NOT EXISTS request_time (
                request_time TIMESTAMP,
                requested_file VARCHAR(255),
                error_code INT
                    )
                """
                )
            )
            conn.commit()
            conn.close()
    except Exception as e:
        console.log(f"Could not create database {e}")
        return Response("Error", status=409, mimetype="text/plain")


def make_database_and_publish_data(
    country,
    gender,
    age,
    income,
    is_banned,
    client_ip,
    time_of_request,
):
    try:
        with pool.connect() as conn:
            conn.execute(
                sqlalchemy.text(
                    """
                        INSERT INTO request (country, gender, age, income, is_banned, client_ip, time_of_request)
                        VALUES (:country, :gender, :age, :income, :is_banned, :client_ip, :time_of_request)
                        """
                ),
                dict(
                    country=country,
                    gender=gender,
                    age=age,
                    income=income,
                    is_banned=is_banned,
                    client_ip=client_ip,
                    time_of_request=time_of_request,
                ),
            )
            conn.commit()
            conn.close()
    except Exception as e:
        return Response("Error", status=409, mimetype="text/plain")


def make_second_database_and_publish_data(
    request_time,
    requested_file,
    error_code,
):
    try:
        with pool.connect() as conn:
            conn.execute(
                sqlalchemy.text(
                    """
                        INSERT INTO request_time (request_time, requested_file, error_code)
                        VALUES (:request_time, :requested_file, :error_code)
                        """
                ),
                dict(
                    request_time=request_time,
                    requested_file=requested_file,
                    error_code=error_code,
                ),
            )
            conn.commit()
            conn.close()
    except Exception as e:
        return Response("Error", status=409, mimetype="text/plain")
