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
    container.download_pages()


# CLI
def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_url", help="url of manifest")
    parser.add_argument("out_dir", help="path to image directory")
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
    download_pages(args.manifest_url, args.out_dir)
    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
