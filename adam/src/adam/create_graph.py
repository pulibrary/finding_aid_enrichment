"""
A console script to create a graph from a manifest URL.
"""

import argparse
import json
import logging
import sys
from urllib.request import urlopen
from adam.container import Container

_logger = logging.getLogger(__name__)

def manifest_id(manifest_url):
    """
    Returns the id from a manifest URI.

    Given:
    https://figgy.princeton.edu/concern/scanned_resources/2a701cb1-33d4-4112-bf5d-65123e8aa8e7/manifest
    Return: 2a701cb1-33d4-4112-bf5d-65123e8aa8e7
    """
    return manifest_url.split('/')[-2]

def output_graph(manifest_url, outfile):
    with urlopen(manifest_url) as url:
        manifest = json.loads(url.read())

    container = Container(manifest)
    container.build_graph()
    container.serialize(outfile)

def parse_args(args):
    """Parse command line parameters"""
    parser = argparse.ArgumentParser(description="Produce a graph from a manifest")
    parser.add_argument(dest="url", help="URL of the manifest")
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
    parser.add_argument('-o', '--outfile',
                        dest="outfile",
                        default=sys.stdout.buffer,
                        help="output file (stdout by default)")

    return parser.parse_args(args)

def setup_logging(log_level):
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=log_level, stream=sys.stdout, format=log_format, datefmt="%Y-%m-%d %H:%M:%S"
        )

def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel)
    output_graph(args.url, args.outfile)

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m foo.skeleton 42
    #
    run()
