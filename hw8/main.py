from typing import Optional

from flask import Flask, Response, request
from google.api_core import exceptions
from google.cloud import logging, pubsub_v1, storage

app = Flask(__name__)


client = logging.Client()
log_name = "requester_countries_logs"
client.setup_logging()
logger = client.logger(log_name)


def make_storage_client() -> storage.Client:
    client = storage.Client().create_anonymous_client()
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
        blob_content = blob.download_as_string()
        logger.log_text("Status: 200")
        return Response(blob_content, status=200, mimetype="text/html")
    except exceptions.NotFound:
        err_msg: str = "Error file not found"
        logger.log_text(f"Error file not found: {err_msg}, Status: 404")
        return Response(err_msg, status=404, mimetype="text/plain")


def get_bucket_path_fname(request_args: dict) -> Optional[str]:
    # "name = bucketname + '/webdir/' + str(idx) + '.html'"
    name = request_args.url
    if name is None:
        return None
    print(name.split("/")[-3:])
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
                    logger.log_text(
                        f"Error, the country of {country} is an enemy country, Status: 400"
                    )
                    return Response(err_msg, status=400, mimetype="text/plain")

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


# sudo journalctl -u google-startup-scripts.service -f
