import apache_beam as beam
import numpy as np
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import storage

MAX_NUM_FILES: int = 10000

input_path = "gs://hw2-arkjain-mini-internet/mini_internet_test/"
output_path = "gs://hw7-ds561-apache-beam/output/"
