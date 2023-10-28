import os
from flask import Flask, Request, Response, request
from google.cloud import storage
from typing import Optional
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud import logging
from google.cloud.sql.connector import Connector
import pymysql
import sqlalchemy
from dotenv import load_dotenv 

load_dotenv()

connector = Connector()
app = Flask(__name__)

INSTANCE_NAME = os.environ["INSTANCE_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

print(INSTANCE_NAME, DB_USER, DB_PASSWORD, DB_NAME)

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
                print("here in if")
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
                store_request_header_for_table["time_of_request"] = request.headers.get(
                    "X-time"
                )
                store_request_header_for_second_table[
                    "request_time"
                ] = request.headers.get("X-time")
                store_request_header_for_second_table["requested_file"] = file
                
                print(f"store_request_header_for_table: {store_request_header_for_table}")
                print(f"store_request_header_for_second_table: {store_request_header_for_second_table}")

                if check_if_country_is_enemy(country):
                    err_msg = f"The country of {country} is an enemy country"
                    store_request_header_for_table["is_banned"] = (country, True)
                    future = publisher.publish(topic_path, err_msg.encode("utf-8"))
                    logger.log_text(
                        f"Error, the country of {country} is an enemy country, Status: 400"
                    )
                    store_request_header_for_second_table["error_code"] = 400
                    return Response(err_msg, status=400, mimetype="text/plain")

                store_request_header_for_table["is_banned"] = (country, False)
                store_request_header_for_second_table["error_code"] = 200
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


def make_database_and_publish_data(
        country,
        gender,
        age,
        income,
        is_banned,
        client_ip,
        time_of_request,
        ):
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
                )
        )
        conn.commit()
        conn.close()

def make_second_database_and_publish_data(
        request_time,
        requested_file,
        error_code,
        ):
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
                )
        )
        conn.commit()
        conn.close()
