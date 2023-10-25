import os
from flask import Flask, Request, Response, request
from google.cloud import storage
from typing import Optional
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud import logging
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy

connector = Connector(
    "cloudcomputingcourse-398918:us-central1:cloudcomputingcourse",
    "pymysql",
    ip_type=IPTypes.PRIVATE,
)
app = Flask(__name__)


def get_connection() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        os.environ["INSTANCE_NAME"],
        "pymysql",
        os.environ["DB_USER"],
        os.environ["DB_PASSWORD"],
        os.environ["DB_NAME"],
    )
    return conn


def make_connection_pool():
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=lambda: get_connection(),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
    )
    return pool


def make_logging_client():
    client = logging.Client()
    log_name = "requester_countries_logs"
    client.setup_logging()
    logger = client.logger(log_name)
    return logger


def make_storage_client() -> storage.Client:
    client = storage.Client().create_anonymous_client()
    return client


def get_files_from_bucket(
    bucket_name: str,
    folder_name: str,
    file_name: str,
) -> Optional[str]:
    logger = make_logging_client()
    try:
        client = make_storage_client()
        prefix: str = f"{folder_name}/{file_name}"
        print("here------")
        blobs = client.list_blobs(bucket_name, prefix=prefix)
        print("Prefix", prefix, "blobs", blobs)
        for blob in blobs:
            print(f"blob name: {blob.name}")
        logger.log_text(
            f"Accessing blob: {blob.name}, and retuning the data to the user {blob.download_as_string()}"
        )
        return Response(blob.download_as_string(), mimetype="text/html")
    except:
        err_msg: str = "Error file not found"
        logger.log_text(f"Error file not found: {err_msg}, Status: 404")
        return Response(err_msg, status=404, mimetype="text/plain")


def get_bucket_path_fname(request_args: dict) -> Optional[str]:
    # "name = bucketname + '/webdir/' + str(idx) + '.html'"
    name = request_args.url
    if name is None:
        return None
    print(name.split("/")[-3:])
    logger = make_logging_client()
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
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        "cloudcomputingcourse-398918", "banned_request_countries"
    )
    logger = make_logging_client()
    print(bucket_name, dir, file)
    try:
        if request.method == "GET":
            requets_headers = dict(request.headers.items())
            print("headers: ", requets_headers)
            store_request_header_for_table = {}
            store_request_header_for_second_table = {}
            if request.headers.get("X-country") is not None:
                country = request.headers.get("X-country")
                store_request_header_for_table["country"] = country
                store_request_header_for_table["gender"] = request.headers.get(
                    "X-gender"
                )
                store_request_header_for_table["age"] = request.headers.get("X-age")
                store_request_header_for_table["income"] = request.headers.get(
                    "X-income"
                )
                store_request_header_for_table["client_ip"] = request.headers.get(
                    "X-client-IP"
                )
                store_request_header_for_second_table[
                    "request_time"
                ] = request.headers.get("X-time")
                store_request_header_for_second_table["requested_file"] = file

                if check_if_country_is_enemy(country):
                    err_msg = f"The country of {country} is an enemy country"
                    store_request_header_for_table["is_banned"] = (country, True)
                    future = publisher.publish(topic_path, err_msg.encode("utf-8"))
                    logger.log_text(
                        f"Error, the country of {country} is an enemy country, Status: 400"
                    )
                    return Response(err_msg, status=400, mimetype="text/plain")

                store_request_header_for_table["is_banned"] = (country, False)
                make_countries_mysql_table(
                    store_request_header_for_table,
                    store_request_header_for_second_table,
                )
            return get_files_from_bucket(bucket_name, dir, file)
        elif request.method != "GET":
            err_msg = "Error, wrong HTTP Request Type"
            print(err_msg)
            logger.log_text(f"Error, wrong HTTP Request Type, Status: 501")
            return Response(err_msg, status=501, mimetype="text/plain")
    except:
        err_msg = "Error, wrong HTTP Request Type"
        # logger.log_text(f"Error, wrong HTTP Request Type, Status: 501")
        return Response(err_msg, status=501, mimetype="text/plain")


"""
First table
Users: countries, gender, age, income, is_banned, client_ip
Second table
Requests: request_time, request_type
"""


def make_countries_mysql_table(data_from_headers: dict, data_from_request: dict):
    
    pool = make_connection_pool()

    with pool.connect() as conn:
        query = """
            CREATE TABLE IF NOT EXISTS Users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    country VARCHAR(255) NOT NULL,
                    client_id INT NOT NULL,
                    gender_req ENUM('Male', 'Female'),
                    age ENUM('0-16', '17-25', '26-35', '36-45', '46-55', '56-65', '66-75', '76+'),
                    income_req ENUM('0-10k', '10k-20k', '20k-40k', '40k-60k', '60k-100k', '100k-150k', '150k-250k', '250k+'),
                    is_banned BOOLEAN NOT NULL,
                    )
            """
        conn.execute(query)

    with pool.connect() as conn:
        query = """
            CREATE TABLE IF NOT EXISTS Requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    time TIMESTAMP NOT NULL,
                    file_requested VARCHAR(255) NOT NULL,
                    )
            """
        conn.execute(query)
    with pool.connect() as connection:
        query = f"""
           INSERT INTO Users(country, client_id, gender, income, age, is_banned)
           VALUES (
               '{data_from_headers["country"]}', 
               '{data_from_headers["client_id"]}', 
               '{data_from_headers["gender"]}', 
               '{data_from_headers["income"]}', 
               '{data_from_headers["age"]}', 
               '{data_from_headers["population"]}', 
               '{int(data_from_headers["is_banned"][1])}'
           )
           """
        connection.execute(query)
    with pool.connect() as connection:
        query = f"""
           INSERT INTO Requests(time, file_requested)
           VALUES (
               '{data_from_request["time"]}', 
               '{data_from_request["file_requested"]}'
           )
           """
        connection.execute(query)
