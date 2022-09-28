import argparse
import logging
from os import defpath
import sys
from pathlib import Path
from adam.manifest import Manifest
from rdflib import container
import spacy
from adam.container import Container

_logger = logging.getLogger(__name__)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_url", help="url of manifest")
    parser.add_argument("nlp", help="name of spacy model to use")
    parser.add_argument("basedir", help="directory to save into")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    _logger.info("Script starts here")
    args = parse_args(args)
    setup_logging(args.loglevel)
    manifest = Manifest(args.manifest_url)
    nlp = spacy.load(args.nlp)
    container = Container(manifest, nlp)
    base_dir = Path(args.basedir)
    base_dir.mkdir(parents=True, exist_ok=True)
    container.dump(base_dir)
    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
