import argparse
import logging
from os import defpath
import sys
from pathlib import Path
import spacy
from adam.container import Container


_logger = logging.getLogger(__name__)

_default_output_dir = Path("/tmp/adam")
_default_output_dir.mkdir(parents=True, exist_ok=True)


def analyze_manifest(
    manifest_url, nlp, out_dir=_default_output_dir, image_dir=_default_output_dir
):
    container = Container(manifest_url, nlp, image_dir)
    container.dump(out_dir)


# CLI
def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_url", help="url of manifest")
    parser.add_argument("nlp", help="name of spacy model to use")
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
    nlp = spacy.load(args.nlp)
    analyze_manifest(args.manifest_url, nlp, _default_output_dir, _default_output_dir)
    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
