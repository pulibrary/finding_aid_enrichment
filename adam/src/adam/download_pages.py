import argparse
import logging
import sys
from pathlib import Path
from adam.container import Container

_logger = logging.getLogger(__name__)

_default_output_dir = Path("/tmp/adam")
_default_output_dir.mkdir(parents=True, exist_ok=True)

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from foo.skeleton import fib`,
# when using this Python module as a library.

def download_pages(manifest_url, out_dir=_default_output_dir):
    container = Container(manifest_url)
    container.download_images()

def analyze_manifest(manifest_url, out_dir=_default_output_dir):
    container = Container(manifest_url)
    container.dump(out_dir)

def analyze_manifests(manifest_list, out_dir):
    with open(manifest_list, 'r') as m:
        manifests = m.readlines()
        for manifest_url in manifests:
            _logger.info(f"processing {manifest_url}")
            container = Container(manifest_url.strip())
            container.dump(out_dir)
            _logger.info(f"done with {manifest_url}")

# CLI


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="source_file")
    parser.add_argument(dest="out_dir")
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
    args = parse_args(args)
    setup_logging(args.loglevel)
    analyze_manifests(args.source_file, args.out_dir)
    _logger.info("Script ends here")


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
