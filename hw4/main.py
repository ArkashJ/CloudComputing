import os
from flask import Flask, Request, Response, request
from google.cloud import storage
from typing import Optional
from google.api_core import exceptions
from google.cloud import pubsub_v1
from google.cloud import logging

app = Flask(__name__)


def make_logging_client() -> logging.logger:
    client = logging.Client()
    log_name = "requester_countries_logs"
    client.setup_logging(log_name)
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
        # for blob in blobs:
        #     print(f"blob name: {blob.name}")
        logger.log_text(f"Accessing blob: {blob.name}, and retuning the data to the user {blob.download_as_string()}")
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
    logger.log_text(f"The url is {name.split('/')[-3:]}"})
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
            if request.headers.get("X-country") is not None:
                country = request.headers.get("X-country")
                print(f"country: ------- {country}")
                if check_if_country_is_enemy(country):
                    err_msg = f"The country of {country} is an enemy country"
                    future = publisher.publish(topic_path, err_msg.encode("utf-8"))
                    logger.log_text(f"Error, the country of {country} is an enemy country, Status: 400")
                    return Response(err_msg, status=400, mimetype="text/plain")

            return get_files_from_bucket(bucket_name, dir, file)
        elif request.method != "GET":
            err_msg = "Error, wrong HTTP Request Type"
            print(err_msg)
            logger.log_text(f"Error, wrong HTTP Request Type, Status: 501")
            return Response(err_msg, status=501, mimetype="text/plain")
    except:
        err_msg = "Error, wrong HTTP Request Type"
        logger.log_text(f"Error, wrong HTTP Request Type, Status: 501")
        return Response(err_msg, status=501, mimetype="text/plain")
