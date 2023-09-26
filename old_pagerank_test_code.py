from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import time
import re
import os
from google.cloud import storage

# from google.oauth2.service_account import Credentials
from itertools import chain
import numpy as np
import networkx as nx
from numba import jit
from tqdm import tqdm

MAX_NUM_FILES: int = 10000
MAX_LINKS: int = 250


## -------------- HELPER FUNCTIONS -------------- ##
# Function to apply regex to get the html file names
# Gets the links from the file in the CLOUD
## NOTE: The logic is different from the local function because you have to open a file and read it locally
def get_html_from_file_cloud(files) -> list[str]:
    reg = r'"\d*.html"'
    pattern = re.compile(reg)
    result = re.findall(pattern, files)
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


# Function to get the links dictionary LOCALLY
def iter_files_and_get_links(
    filepath: str = "mini_internet",
):
    # Function to apply regex to get the html file names
    def get_html_from_file(files) -> list[str]:
        reg = r'"\d*.html"'
        pattern = re.compile(reg)
        with open(files, "r", encoding="utf-8") as f:
            html = f.read()
            result = re.findall(pattern, html)
            return result, len(result)

    incoming_links = []
    outgoing_links = []
    #  Logic to iterate through the files and get the links
    links_dict = {}
    for i in tqdm(range(MAX_NUM_FILES)):
        if os.path.exists(f"{filepath}/{i}.html"):
            html_link_res, res_len = get_html_from_file(f"{filepath}/{i}.html")
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


## -------------- MAIN CLASS TO USE HELPERS & FIND PAGE RANK AND STATISTICS -------------- ##
class Pagerank_class:
    """
    These functions do the following:
        - iter_files_and_get_links: iterates through the files and gets the links. It makes a dictionary with
            the key as the page number and the value as the corresponding list of links
        - construct_adjacency_matrix: constructs the adjacency matrix using the links dictionary
        - pagerank: runs the pagerank algorithm on the adjacency matrix
           - We sort the page rank matrix and get the top 5 pages with the highest page rank
        - statistics: prints the statistics for the outgoing and incoming links
        - start, end: to calculate the time taken to run the pagerank algorithm
    """

    def __init__(self, dict=dict[int, list[int]]):
        self.dict = dict

    # Function to iterate through the files and get the links
    def get_links_and_make_adjcency_matrix(self) -> list[list[int]]:
        get_links_dict = iter_files_and_get_links()
        self.dict = get_links_dict
        return self.get_adjacency_mat(get_links_dict)

    # Function to get the adjacency matrix from the links dictionary
    def get_adjacency_mat(self, dict_links: dict[int, list[int]]) -> list[list[int]]:
        adj_mat = construct_adjacency_matrix(dict_links)
        return adj_mat

    # Function to get the top 5 pages with the highest page rank
    def get_page_rank_and_return_top_5(self, adj_mat: list[list[int]]) -> None:
        mat, page_rank = pagerank(adj_mat)
        sorted_mat = np.argsort(mat)
        top_5 = sorted_mat[-5:]
        top_5 = top_5[::-1]
        print(f"\nThe top 5 pageranks are {top_5}\n")

    # Function to print the MEAN, MEDIAN, MAX, MIN and QUINTILES for the outgoing and incoming links
    def print_statistics(self, adj_mat: list[list[int]]):
        statistics(adj_mat)

    # Function to print the time taken
    def print_time_taken(self, start: float, end: float) -> None:
        print(f"\n Time taken: [Fetch Pagerank & Statistics]: {end - start}")

    # Function to test the output:
    def test_output(self):
        """
        Function to test the output by doing the following:
        - making a bi directional graph using the links dictionary from the networkx library
        - running page rank on the graph with alpha = 0.85
        - printing the top 10 pages with the highest page rank
        ## NOTE: The accuracy may vary because we have set our epsilon to 0.005, changing it to 0.0001 will give us a more accurate result
        """
        get_links_dict = self.dict
        # G = nx.Graph(get_links_dict)
        g2 = nx.DiGraph(get_links_dict)
        pr = nx.pagerank(g2, alpha=0.85)
        print(f"Running pagerank using networkx library: \n")
        print(sorted(pr.items(), key=lambda x: x[1], reverse=True)[:5])

    # Function to run the algorithm and print the time taken
    def calculate_pagerank_and_stats_with_running_time(self) -> None:
        adj_mat = self.get_links_and_make_adjcency_matrix()
        start = time.perf_counter()
        self.get_page_rank_and_return_top_5(adj_mat)
        self.print_statistics(adj_mat)
        end = time.perf_counter()
        self.print_time_taken(start, end)

    def calculate_pagerank_on_cloud(self, dict_links: dict[int, list[int]]) -> None:
        adj_mat = self.get_adjacency_mat(dict_links)
        start = time.perf_counter()
        self.get_page_rank_and_return_top_5(adj_mat)
        self.print_statistics(adj_mat)
        end = time.perf_counter()
        self.print_time_taken(start, end)


def run_page_rank_locally():
    local = Pagerank_class()
    local.calculate_pagerank_and_stats_with_running_time()


def run_page_rank_with_tests():
    local = Pagerank_class()
    local.calculate_pagerank_and_stats_with_running_time()
    local.test_output()


def get_bucket_and_block(
    filename: str = "cloudcomputingcourse-398918-79ae91e1fff7.json",
    project: str = "CloudComputingCourse",
    bucket_name: str = "hw2-arkjain-mini-internet",
    block_name: str = "mini_internet",
    max_timeout: int = 30,
):
    # credentials = Credentials.from_service_account_file(
    #     filename=filename,
    # )

    storage_client = storage.Client().create_anonymous_client()

    # print out bucket info
    bucket = storage_client.bucket(bucket_name)
    print(bucket.blob(block_name))
    # work with blobs
    blobs = list(bucket.list_blobs(
        bucket_name, timeout=max_timeout, prefix=block_name
    ))

    def read_blob_and_run_pagerank(blob):
        i = 0
        with blob.open("r") as f:
            #  Logic to iterate through the files and get the links
            html_link_res, res_len = get_html_from_file_cloud(f.read())
            links_dict_elem = list(chain.from_iterable(get_link_id_from_string(html_link_res)))
            return links_dict_elem

    links_dict = {}
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
        arr = tqdm(executor.map(read_blob_and_run_pagerank, blobs), total=MAX_NUM_FILES)
        print(len(arr))
        for i, elem in enumerate(arr):
            links_dict[i] = elem
    page_rank_calculator_class = Pagerank_class(links_dict)
    page_rank_calculator_class.calculate_pagerank_on_cloud(links_dict)


def run_page_rank_cloud():
    get_bucket_and_block()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run the pagerank algorithm locally",
    )
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Run the pagerank algorithm on the cloud",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the pagerank algorithm locally and test the output",
    )
    args = parser.parse_args()
    if args.local:
        run_page_rank_locally()
    if args.cloud:
        run_page_rank_cloud()
    if args.test:
        run_page_rank_with_tests()


main()
