import sys
import json
import logging
from os.path import exists
from pathlib import Path
from urllib.request import urlopen
from adam.container import Container
from adam.collection import Collection

_logger = logging.getLogger(__name__)

def setup_logging(log_level):
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level= log_level, stream=sys.stdout, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
        )


mc076_path = "/Users/cwulfman/repos/github/pulibrary/finding_aid_enrichment/adam/manifest"

target_dir = Path.home() / "Desktop/training3"

with open(mc076_path) as file:
    manifest = json.load(file)

collection = Collection(manifest)

setup_logging(logging.INFO)

logging.debug("starting to iterate over containers")
for container in collection.containers:
    logging.info(f"looking at {container}")
    container.export(target_dir, format="jsonl")
