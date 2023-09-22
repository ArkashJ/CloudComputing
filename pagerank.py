import re
import os
from google.cloud import storage
from google.oauth2.service_account import Credentials

MAX_NUM_FILES: int = 10000
MAX_LINKS: int = 250


def get_bucket_and_block(
    filename: str = "cloudcomputingcourse-398918-79ae91e1fff7.json",
    project: str = "CloudComputingCourse",
    bucket_name: str = "hw2-arkjain-mini-internet",
    block_name: str = "mini_internet",
    max_timeout: int = 10,
):
    credentials = Credentials.from_service_account_file(
        filename=filename,
    )

    storage_client = storage.Client(project=project, credentials=credentials)

    # print out bucket info
    bucket = storage_client.get_bucket(bucket_name, timeout=max_timeout)
    print(bucket.blob(block_name))
    # work with blobs
    blob = storage_client.list_blobs(
        bucket_name, timeout=max_timeout, prefix=block_name
    )

    for blob in blob:
        with blob.open("r") as f:
            print(f.read())


def iter_files_and_get_links():
    # Function to apply regex to get the html file names
    def get_html_from_file(files) -> list[str]:
        reg = r'"\d*.html"'
        pattern = re.compile(reg)
        with open(files, "r", encoding="utf-8") as f:
            html = f.read()
            result = re.findall(pattern, html)
            return result, len(result)

    # Function to iterate through the list of links and only get the page number from the link
    def get_link_id_from_string(list_links: list[str]) -> list[str]:
        reg_str = r"\d+"  # get number from '"8144.html"
        pattern = re.compile(
            reg_str
        )  # compile = efficient way for regex to prevent regex object creation everytime
        result = []
        for link in list_links:
            result.append(re.findall(pattern, link))
        return result, len(result)

    #  Logic to iterate through the files and get the links
    for i in range(MAX_NUM_FILES):
        if os.path.exists(f"mini_internet/{i}.html"):
            html_link_res, res_len = get_html_from_file(f"mini_internet/{i}.html")
            print(res_len, get_link_id_from_string(html_link_res))


if __name__ == "__main__":
    iter_files_and_get_links()
