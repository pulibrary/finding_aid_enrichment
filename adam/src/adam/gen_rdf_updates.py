##
# Basic script to generate new ttl files
# using new CRM encoding.
# Using dump_correspondence.py as a model
from pathlib import Path
from sys import stdout
import logging
import spacy
from adam.container import Container


_logger = logging.getLogger(__name__)

def setup_logging(log_level):
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level= log_level, stream=stdout, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
        )

setup_logging(logging.INFO)

nlp = spacy.load("en_core_web_lg")

cache_path = Path("/Users/cwulfman/Desktop/correspondence_data")

def update_rdf(manifest_url, to_dir):
    container = Container(manifest_url, nlp, cache_path)
    container_label = container.container_label
    print("updating %s" % container_label)
    logging.info("updating %s" % container_label)
    container.build_graph()
    rdf_file_name = container_label + '.' + 'ttl'
    container.serialize(Path(to_dir) / Path(rdf_file_name))
    print("finished updating %s" % container_label)
    logging.info("finished updating %s" % container_label)


output_path = Path("/Users/cwulfman/Desktop/correspondence_data/rdf")
with open('corresp.txt', 'r', encoding="utf-8") as file:
    manifests = file.readlines()
    for manifest_url in manifests:
        update_rdf(manifest_url.strip(), output_path)
