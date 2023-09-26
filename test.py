from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import time
import re
import os
from google.cloud import storage
from itertools import chain
import numpy as np
import networkx as nx
from numba import jit
from tqdm import tqdm
from typing import Optional

MAX_NUM_FILES: int = 10000


def extract_numbers_from_html(
    html_file_path: str,
    pattern: str = r'HREF="(\d+)\.html"',
) -> Optional[list[int]]:
    try:
        with open(html_file_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()
            pattern = pattern
            matches = re.findall(pattern, html_content)
            if matches:
                return [int(match) for match in matches], html_file_path
            else:
                return [], html_file_path
    except FileNotFoundError:
        print(f"File '{html_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def run_files_cloud(
    bucket_name: str = "hw2-arkjain-mini-internet",
    blob_prefix: str = "mini_internet_test/",
    links_dict: dict[int, list[int]] = {},
) -> list[list[int]]:
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=blob_prefix))
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
        futures = [
            executor.submit(extract_numbers_from_html, blob.name) for blob in blobs
        ]

        total_len = len(futures)
        for future in tqdm(
            as_completed(futures),
            total=total_len,
            desc="Extracting numbers from html files",
        ):
            arr, file_path = future.result()
            if arr is []:
                continue
            iter = int(file_path.split("/")[-1].split(".")[0])
            links_dict[iter] = arr
    return links_dict


def run_files_local(
    filepath: str = "mini_internet_test/",
    links_dict: dict[int, list[int]] = {},
) -> list[list[int]]:
    for paths in tqdm(range(MAX_NUM_FILES)):
        html_file_path = f"{filepath}" + str(paths) + ".html"
        numbers, paths_r = extract_numbers_from_html(html_file_path)
        if numbers is []:
            continue
        links_dict[paths] = numbers
    return links_dict


# Function to construct the adjacency matrix given the links dictionary
def construct_adjacency_mat(
    links_dict: dict[int, list[int]] = {},
) -> np.ndarray:
    """
    Description:
    - We construct the adjacency matrix by iterating through the links dictionary
    - For each key(row), we iterate through the values(columns) and set the corresponding index in the adjacency matrix to 1
     when there is a link from the key to the value
    """
    adj_mat = np.zeros((MAX_NUM_FILES, MAX_NUM_FILES))
    for key, value in links_dict.items():
        for val in value:
            adj_mat[key][val] = 1
    return adj_mat


@jit(nopython=True)
def pagerank(
    adj_mat: list[list[int]],
    pr_addition_const: float = 0.15,
    pr_damping_factor: float = 0.85,
    epsilon: float = 0.005,
) -> list[float]:
    """
    Descriptions:
    In a while loop, for each incoming edge i in the 10000, you pick the outgoing edge j and sum the number for this edge,
    adding it to get the total number of outgoing edges for the page.
    #  PR(A) = 0.15 + 0.85 * (PR(T1)/C(T1) + ... + PR(Tn)/C(Tn))

    Explanation:
    - For each "iteration" of the while loop, we update the pagerank matrix for all MAX_NUM_FILES pages
        and then we check if the percent change between the old and new pagerank matrix is less than epsilon
    - If the percent change is less than epsilon, we return the pagerank matrix
    """
    page_rank_mat = np.array([1 / MAX_NUM_FILES] * MAX_NUM_FILES)
    num_iters = 0
    elems_dict = {}
    for i in range(MAX_NUM_FILES):
        elems_dict[i] = np.where(adj_mat[:, i] == 1)[0]

    sums_dict = {}
    for elem in elems_dict:
        sums_dict[elem] = adj_mat[elem].sum()

    # To save time complexity, we precompute:
    # a) For the each of the COLUMNS (incoming links), where the value is 1. MEANING? The page has an incoming link from the column
    # b) For each of the ROWS (outgoing links) in the array of THE CORRESPONDING column key in the dictionary, we sum the outgoing links for that page
    # c) We then divide the pagerank of the incoming link by the sum of the outgoing links for that page
    while True:
        old_mat = page_rank_mat.copy()

        for i in range(MAX_NUM_FILES):
            sum_rows = 0.0
            for elem in elems_dict[i]:
                # For each column, we get the page rank and divide it by the sum of the outgoing links for that page
                sum_rows += page_rank_mat[elem] / sums_dict[elem]
            # Page rank calculation.
            page_rank_mat[i] = pr_addition_const + (pr_damping_factor * sum_rows)
        num_iters += 1
        # get the sum of the updated page rank matrix and the old page rank matrix, to calculate the percent change < epsilon
        page_rank_mat_sum = page_rank_mat.sum()
        old_mat_sum = old_mat.sum()
        percent_change = abs(page_rank_mat_sum - old_mat_sum) / old_mat_sum
        print(
            f"Num iters: {num_iters}",
        )
        if percent_change <= epsilon:
            return old_mat, page_rank_mat


def page_rank_cloud_computer():
    links_dict = run_files_cloud()
    adj_mat = construct_adjacency_mat(links_dict)
    start = time.perf_counter()
    pr, pg = pagerank(adj_mat)
    args_m = np.argsort(pr)
    args_m = args_m[-5:][::-1]
    print("\n", args_m, "\n")
    for i in range(len(args_m)):
        print(f"Page {i}: {args_m[i]}, Pagerank value: {pg[args_m[i]]} \n")
    statistics(adj_mat)
    end = time.perf_counter()
    print(f"\nTime taken: {end - start}")

def page_rank_local_computer():
    links_dict = run_files_local()
    adj_mat = construct_adjacency_mat(links_dict)
    start = time.perf_counter()
    pr, pg = pagerank(adj_mat)
    args_m = np.argsort(pr)
    args_m = args_m[-5:][::-1]
    print(args_m)
    for i in range(len(args_m)):
        print(f"Page {i}: {args_m[i]}, Pagerank value: {pg[args_m[i]]}")
    statistics(adj_mat)
    end = time.perf_counter()
    print(f"Time taken: {end - start}")

def statistics(adj_mat: list[list[int]]):
    outgoing_links = [0] * MAX_NUM_FILES
    incoming_links = [0] * MAX_NUM_FILES

    for i in range(MAX_NUM_FILES):
        outgoing_links[i] = adj_mat[i, :].sum()
        incoming_links[i] = adj_mat[:, i].sum()

    def laverage(lst):
        return sum(lst) / len(lst)

    def lmedian(lst):
        return sorted(lst)[len(lst) // 2]

    def lmax(lst):
        return max(lst)

    def lmin(lst):
        return min(lst)

    def quintiles(lst):
        return np.quantile(lst, [0.2, 0.4, 0.6, 0.8, 1])

    print(
        f"\t \t Outgoing Links Data: \t \t \n",
        f"Average: {laverage(outgoing_links)} \n",
        f"Median: {lmedian(outgoing_links)} \n",
        f"Max: {lmax(outgoing_links)} \n",
        f"Min: {lmin(outgoing_links)} \n",
        f"Quintiles: {quintiles(outgoing_links)} \n",
    )
    print(
        f"\t \t Incoming Links Data: \t \t \n",
        f"Average: {laverage(incoming_links)} \n",
        f"Median: {lmedian(incoming_links)} \n",
        f"Max: {lmax(incoming_links)} \n",
        f"Min: {lmin(incoming_links)} \n",
        f"Quintiles: {quintiles(incoming_links)} \n",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Run the pagerank algorithm on the cloud",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run the pagerank algorithm on the local machine",
    )
    parser.add_argument(
            "--test",
            action="store_true",
            help="Run the pagerank algorithm on the local machine and cloud",
        )
    args = parser.parse_args()
    if args.cloud:
        page_rank_cloud_computer()
    elif args.local:
        page_rank_local_computer()
    else:
        page_rank_cloud_computer()
        page_rank_local_computer()

main()
