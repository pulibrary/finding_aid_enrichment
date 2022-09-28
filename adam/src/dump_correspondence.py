from pathlib import Path
from sys import stdout
import logging
import spacy
from adam.container import Container

_logger = logging.getLogger(__name__)


def setup_logging(log_level):
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=log_level, stream=stdout, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
    )


setup_logging(logging.INFO)

nlp = spacy.load("en_core_web_lg")

output_path = Path("/Users/cwulfman/Desktop/correspondence_data")
with open("corresp.txt", "r", encoding="utf-8") as file:
    manifests = file.readlines()
    for manifest_url in manifests:
        container = Container(manifest_url, nlp)
        container_label = container.label
        logging.info("starting dump of %s" % container_label)
        container.dump(output_path)
        logging.info("finished dump of %s" % container_label)
