import os
from flask import Flask
from google.cloud import storage
from typing import Optional
from google.api_core import exceptions
from google.cloud import pubsub_v1

app = Flask(__name__)

def make_storage_client() -> storage.Client:
    client = storage.Client().create_anonymous_client()
    return client


def get_files_from_bucket(
    bucket_name: str,
    folder_name: str,
    file_name: str,
) -> Optional[str]:
    try:
        client = storage.Client().create_anonymous_client()
        prefix: str = f"{folder_name}{file_name}"
        blobs = client.list_blobs(bucket_name, prefix=prefix)
        for blob in blobs:
            print(f"blob name: {blob.name}")
        return flask.Response(blob.download_as_string(), mimetype="text/html")
    except:
        err_msg: str = "Error file not found"
        return flask.Response(err_msg, status=404, mimetype="text/plain")


def get_bucket_path_fname(request_args: dict) -> Optional[str]:
    # "name = bucketname + '/webdir/' + str(idx) + '.html'"
    name = request_args.url
    print("original name: ", name)
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

@app.route("/fetch", methods=["GET"])
def receive_http_request(
    request: flask.Request,
) -> Optional[flask.Response]:
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        "cloudcomputingcourse-398918", "banned_request_countries"
    )

    try:
        if request.method == "GET":
            requets_headers = dict(request.headers.items())
            if request.headers.get("X-country") is not None:
                country = request.headers.get("X-country")
                print(f"country: ------- {country}")
                if check_if_country_is_enemy(country):
                    err_msg = f"The country of {country} is an enemy country"
                    future = publisher.publish(topic_path, err_msg.encode("utf-8"))
                    return flask.Response(err_msg, status=400, mimetype="text/plain")

            bucket_name, path_name, fname = get_bucket_path_fname(request)
            return get_files_from_bucket(bucket_name, "mini_internet_test/", fname)
        elif request.method != "GET":
            err_msg = "Error, wrong HTTP Request Type"
            print(err_msg)
            return flask.Response(err_msg, status=501, mimetype="text/plain")
    except:
        err_msg = "Error, wrong HTTP Request Type"
        return flask.Response(err_msg, status=501, mimetype="text/plain")
