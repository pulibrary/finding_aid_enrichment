"""Loads directory of Turtle files into GraphDB


"""

import sys
from pathlib import Path
import argparse
import requests

def load_ttl_file(path):
    headers = {"Content-Type": "application/x-turtle"}
#    url = "http://localhost:7200/repositories/Kennan_subseries_1A/statements"
    url = "http://localhost:7200/repositories/test_kennan/statements"

    with open(path, 'rb') as f:
        print(path)
        response = requests.post(url, headers=headers, data=f)
    return response

def file_list(path):
    p = Path(path)
    return p.glob("**/*.ttl")


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="upload turtle files")
    parser.add_argument('source_dir')
    return parser.parse_args(args)

def main(args):
    args = parse_args(args)
    files = file_list(args.source_dir)
    for f in files:
        print(f"loading {f}")
        load_ttl_file(f)

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
