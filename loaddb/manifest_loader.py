# The ManifestLoader module

"""
A ManifestLoader object is used to load a IIIF manifest into a
GraphDB repository.

THIS ONE WORKS

Usage:

  manifest_url = 'https://figgy.princeton.edu/concern/scanned_resources/2a701cb1-33d4-4112-bf5d-65123e8aa8e7/manifest'
p
  repository = "cold_war_papers"

  server_url = "http://localhost:7200"

  loader = ManifestLoader(manifest_url, repository, server_url)

  response = loader.load()
"""

import sys
from pathlib import Path
import argparse
import json
from sys import stdout
import logging
import requests


class ManifestLoader:
    """Loads a manifest into GraphDB via its
    rest interface."""

    def __init__(self, url, repository, server_url="http://localhost:7200"):
        self._base_url = server_url + "/rest/data/import/upload"
        self._data = {}
        self._headers = {}
        self._repository = repository
        self.set_default_headers()
        self.set_default_data()
        self._data['data'] = url
        self._data['name'] = url

    def set_default_headers(self):
        self._headers['Content-Type'] = 'application/ld+json'

    def set_default_data(self):
        self._data = {"replaceGraphs": [],
                      "baseURI": None,
                      "forceSerial": False,
                      "type": "url",
                      "format": "application/ld+json",
                      "parserSettings": {"preserveBNodeIds": False,
                                         "failOnUnknownDataTypes": False,
                                         "verifyDataTypeValues": False,
                                         "normalizeDataTypeValues": False,
                                         "failOnUnknownLanguageTags": False,
                                         "verifyLanguageTags": True,
                                         "normalizeLanguageTags": False,
                                         "stopOnError": True},
                      "requestIdHeadersToForward": None}

    @property
    def repository(self):
        return self._repository

    @repository.setter
    def repository(self, repository_id):
        self._repository = repository_id

    @property
    def url(self):
        if not self._repository:
            raise ValueError("no repository specified")
        return "/".join((self._base_url, self._repository, "url"))

    @property
    def data(self):
        return json.dumps(self._data)

    @property
    def headers(self):
        return self._headers

    def load(self):
        response = requests.post(self.url,
                                 headers=self.headers,
                                 data=self.data)
        return response


# CLI

def parse_args(args):
    parser = argparse.ArgumentParser(
        description="upload manifests from list of manifests")
    parser.add_argument('manifest_list')
    parser.add_argument('repository')
    parser.add_argument('server')
    return parser.parse_args(args)

def main(args):
    args = parse_args(args)
    _logger = logging.getLogger(__name__)
    log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=logging.INFO,
                        stream=stdout,
                        format=log_format,
                        datefmt="%Y-%m-%d %H:%M:%S")

    with open(args.manifest_list, 'r', encoding="utf-8") as file:
        manifests = file.readlines()
        for manifest_url in manifests:
            logging.info("loading %s" % manifest_url)
            result = ManifestLoader(manifest_url,
                                    args.repository,
                                    args.server).load()
            logging.info("result: %s" % result)

def run():
    main(sys.argv[1:])

if __name__ == "__main__":
    run()
