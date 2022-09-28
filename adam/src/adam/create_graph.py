"""
A console script to create a graph from a manifest URL.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from adam.manifest import Manifest
from adam.container import Container
from rdflib import container

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters"""
    parser = argparse.ArgumentParser(description="Produce a graph from a manifest")
    parser.add_argument("url", help="URL of the manifest")
    parser.add_argument("outdir", help="output directory")
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


def setup_logging(log_level):
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    container = Container(Manifest(args.url))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for page in container.pages:
        page.export_as_rdf(outdir)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
