import argparse
import re

import apache_beam as beam
import numpy as np
from apache_beam.io import ReadFromText
from apache_beam.io.fileio import MatchAll, MatchFiles, ReadMatches
from apache_beam.io.textio import WriteToText
from apache_beam.options.pipeline_options import (GoogleCloudOptions,
                                                  PipelineOptions,
                                                  SetupOptions,
                                                  StandardOptions)
from google.cloud import logging, storage

MAX_NUM_FILES: int = 10000

input_path = "gs://hw7-ds561-apache-beam/mini_internet_test/"
output_path = "gs://hw7-ds561-apache-beam/output/"


class ExtractHTMLLinks(beam.DoFn):
    def process(self, element):
        file_name, file_content = element
        pattern = re.compile(r'<a HREF="(\d+).html">')
        file_content = file_content.decode("utf-8")
        links = re.findall(pattern, file_content)
        # for each link, we get the file number and link
        for link in links:
            f_path = file_name.split("/")[-1]
            f_name = f_path.split(".")[0]
            yield f_name, link


class CountIncomingLinks(beam.DoFn):
    def process(self, element):
        file_name, file_content = element
        pattern = re.compile(r'<a HREF="(\d+).html">')
        file_content = file_content.decode("utf-8")
        links = pattern.findall(file_content)
        for link in links:
            f_path = link.split(".")[0]
            # for each link, assign the value of 1 per each occurence
            # later on we shall sum the values to get the total number of incoming links
            yield f_path, 1


def main(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        dest="input_path",
        default=input_path,
        help="Input file to process.",
    )

    parser.add_argument(
        "--output",
        dest="output_path",
        default=output_path,
        help="Output file to write results to.",
    )

    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    # for local testing
    # pipeline_options.view_as(StandardOptions).runner = "DirectRunner"

    # for cloud testing
    pipeline_options.view_as(StandardOptions).runner = "DirectRunner"

    google_cloud_options = pipeline_options.view_as(GoogleCloudOptions)
    google_cloud_options.project = "cloudcomputingcourse-398918"
    google_cloud_options.region = "us-central1"
    google_cloud_options.job_name = "count-links-in-mini-internet"
    google_cloud_options.staging_location = "gs://hw7-ds561-apache-beam/staging"
    google_cloud_options.temp_location = "gs://hw7-ds561-apache-beam/temp"
    google_cloud_options.service_account_email = (
        "ds561-hw7-acc@cloudcomputingcourse-398918.iam.gserviceaccount.com"
    )
    setup_options = pipeline_options.view_as(SetupOptions)
    setup_options.requirements_file = "./requirements.txt"

    with beam.Pipeline(options=pipeline_options) as p:
        # extract the file name and file content
        get_files_from_bucket = (
            p
            | "Get files from bucket" >> MatchFiles(known_args.input_path + "*.html")
            | "Read file contents" >> ReadMatches()
            | "Decode file contents" >> beam.Map(lambda x: (x.metadata.path, x.read()))
        )
        extract_links = get_files_from_bucket | "Extract outgoing links" >> beam.ParDo(
            ExtractHTMLLinks()
        )

        count_links = extract_links | "Count the links" >> beam.combiners.Count.PerKey()
        top_links = (
            count_links
            | "Get top 5 links"
            >> beam.transforms.combiners.Top.Of(5, key=lambda x: x[1])
            | "Write to file"
            >> WriteToText(f"{known_args.output_path}/outgoing_links.txt")
            | "Print top 5 links" >> beam.Map(print)
        )

        extract_incoming_links = (
            get_files_from_bucket
            | "Extract incoming links" >> beam.ParDo(CountIncomingLinks())
        )
        count_incoming_links = (
            extract_incoming_links | "Reduce the keys" >> beam.combiners.Count.PerKey()
        )
        top_incoming_links = (
            count_incoming_links
            | "Count frequency of top 5 links"
            >> beam.transforms.combiners.Top.Of(5, key=lambda x: x[1])
            | "Write to incoming file"
            >> WriteToText(f"{known_args.output_path}/incoming_links.txt")
            | "Print top 5 incoming links" >> beam.Map(print)
        )


if __name__ == "__main__":
    main()
