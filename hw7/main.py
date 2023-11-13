import argparse
import re

import apache_beam as beam
import numpy as np
from apache_beam.io import ReadFromText
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import storage

MAX_NUM_FILES: int = 10000

input_path = "gs://hw2-arkjain-mini-internet/mini_internet_test/"
output_path = "gs://hw7-ds561-apache-beam/output/"

beam_options = PipelineOptions(
    runner="DataflowRunner",
    project="cloudcomputingcourse-398918",
    job_name="count-links-in-mini-internet",
    temp_location="gs://hw7-ds561-apache-beam/temp/",
)

pipeline = beam.Pipeline(options=beam_options)


class ExtractHTMLLinks(beam.DoFn):
    def process(self, element):
        file_name, file_content = element
        pattern = re.compile(r'a< HREF="(\d+).html">')
        links = pattern.findall(file_content)
        # for each link, we get the file number and link
        for link in links:
            f_path = file_name.split("/")[-1].split(".")[0]
            yield f_path, link


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
    pipeline_options.view_as(StandardOptions).runner = "DirectRunner"

    with beam.Pipeline(options=pipeline_options) as p:
        lines = p | ReadFromText(known_args.input_path)
