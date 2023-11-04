import csv
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import pymysql
import sqlalchemy
from dotenv import load_dotenv
from flask import Flask, Response, request
from google.api_core import exceptions
from google.cloud import storage
from google.cloud.sql.connector import Connector

load_dotenv()

connector = Connector()

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


def get_data():
    try:
        print("establishing connection")
        with pool.connect() as conn:
            #res = conn.execute(sqlalchemy.text("SELECT * FROM `request`")).fetchall()
            res = conn.execute(sqlalchemy.text("SELECT * FROM `request_time`")).fetchall()
            with open("failure.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(res)
            conn.commit()
            conn.close()
            print("connection closed")
    except exceptions.GoogleAPIError as err:
        print(err)
        return None


def main():
    print(get_data())


main()
