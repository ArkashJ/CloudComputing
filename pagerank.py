import re
import os
from google.cloud import storage
from google.oauth2.service_account import Credentials
from itertools import chain
import numpy as np
import networkx as nx
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
        return result

    #  Logic to iterate through the files and get the links
    links_dict = {}
    for i in range(MAX_NUM_FILES):
        if os.path.exists(f"test/{i}.html"):
            html_link_res, res_len = get_html_from_file(f"test/{i}.html")
            links_dict[i] = list(
                chain.from_iterable(get_link_id_from_string(html_link_res))
            )
    return links_dict


def construct_adjacency_matrix(links_dict: dict) -> list[list[int]]:
    # The rows in the matrix are the outgoing links and the columns are the incoming links
    # if the row has a 1, it means that the column has a link to the row otherwise 0
    adj_mat = np.array(
        [[0 for i in range(MAX_NUM_FILES)] for j in range(MAX_NUM_FILES)]
    )
    for key, value in links_dict.items():
        curr_row = adj_mat[key]
        for link in value:
            curr_row[int(link)] = 1
    return adj_mat


def pagerank(
    adj_mat: list[list[int]],
    pr_addition_const: float = 0.15,
    pr_damping_factor: float = 0.85,
    epsilon: float = 0.005,
) -> list[float]:
    #  PR(A) = 0.15 + 0.85 * (PR(T1)/C(T1) + ... + PR(Tn)/C(Tn))
    page_rank_mat = np.array([1 / MAX_NUM_FILES] * MAX_NUM_FILES)
    """
    In a double for loop, for each incoming edge i in the 10000,
    you pick the outgoing edge j and sum the number for this edge,
    adding it to get the total number of outgoing edges for the page.
    """
    num_iters = 0
    elems_dict = {}
    for i in range(MAX_NUM_FILES):
        elems_dict[i] = np.where(adj_mat[:, i] == 1)[0]
    
    sums_dict = {}
    for elem in elems_dict:
        sums_dict[elem] = adj_mat[elem].sum()

    while True:
        old_mat = page_rank_mat.copy()

        for i in range(MAX_NUM_FILES):
            sum_rows = 0.0
            for elem in elems_dict[i]:
                sum_rows += page_rank_mat[elem] / sums_dict[elem]

            page_rank_mat[i] = pr_addition_const + (pr_damping_factor * sum_rows)
        num_iters += 1
        page_rank_mat_sum = page_rank_mat.sum()
        old_mat_sum = old_mat.sum()
        percent_change = abs(page_rank_mat_sum - old_mat_sum) / old_mat_sum
        print(
            f"Percent change: {percent_change}",
            f"Num iters: {num_iters}",
            f"Sum of page rank mat: {page_rank_mat_sum}",
            f"Sum of old mat: {old_mat_sum}",
        )
        if percent_change <= epsilon:
            return old_mat


def main():
    get_links_dict = iter_files_and_get_links()
    adj_mat = construct_adjacency_matrix(get_links_dict)
    mat = pagerank(adj_mat)
    sorted_mat = np.argsort(mat)
    print(sorted_mat[:10])
    
    # G = nx.Graph(get_links_dict)
    # g2 = nx.DiGraph(get_links_dict)
    # pr = nx.pagerank(g2, alpha=0.85)
    # print(sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10])
main()
