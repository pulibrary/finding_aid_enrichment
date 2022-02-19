import sys
import json
import logging
from pathlib import Path
from urllib.request import urlopen
from adam.container import Container
from adam.collection import Collection

_logger = logging.getLogger(__name__)

def setup_logging(log_level):
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=log_level, stream=sys.stdout, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
        )


mc076_path = "/Users/cwulfman/repos/github/pulibrary/finding_aid_enrichment/adam/manifest"

done_dir = Path("/Users/cwulfman/Desktop/cw_graphs_1")
target_dir = Path.home() / "Desktop/cw_graphs"
temp_dir = Path("/tmp")

with open(mc076_path) as file:
    manifest = json.load(file)

collection = Collection(manifest)

setup_logging(logging.DEBUG)

logging.debug("starting to iterate over containers")
for container in collection.containers:
    logging.debug(f"looking at {container}")
    c_id = container.manifest['@id'].split('/')[-2]
    fp = done_dir / Path(c_id + ".ttl")
    if fp.exists():
        logging.info(f"{id} already exists")
    else:
        target = target_dir / Path(c_id + ".ttl")
        logging.info(f"creating {c_id}")
        container.build_graph()
        container.serialize(target)
        logging.info(f"finished {c_id}")
