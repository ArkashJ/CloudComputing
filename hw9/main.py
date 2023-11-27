import os
from typing import Optional

from flask import Flask, Response, request
from google.api_core import exceptions
from google.cloud import compute_v1, logging, pubsub_v1, storage

app = Flask(__name__)


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
        bucket = client.bucket(bucket_name)
        prefix = folder_name + "/" + file_name
        blobs = bucket.blob(prefix)
        if blobs.exists():
            print("File exists")
            return Response(blobs.download_as_string(), mimetype="text/html")
    except exceptions.NotFound:
        err_msg: str = "Error file not found"
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
    if country in LIST_OF_ENEMY_COUNTRIES:
        return True
    return False


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
            request_headers = dict(request.headers.items())
            print("headers: ", request_headers)
            if request.headers.get("X-Country") is not None:
                country = request.headers.get("X-Country")
                print("Checking if the country is an enemy ", country)
                if check_if_country_is_enemy(country):
                    err_msg = f"The country of {country} is an enemy country"
                    publisher.publish(topic_path, err_msg.encode("utf-8"))
                    print("published")
                    return Response(err_msg, status=400, mimetype="text/plain")
                print("Country is not an enemy country")
            return get_files_from_bucket(bucket_name, dir, file)
        elif request.method != "GET":
            err_msg = "Error, wrong HTTP Request Type"
            print(err_msg)
            return Response(err_msg, status=501, mimetype="text/plain")
    except:
        err_msg = "Error, wrong HTTP Request Type"
        return Response(err_msg, status=501, mimetype="text/plain")
