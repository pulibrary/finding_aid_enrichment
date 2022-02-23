"""The adam Container module

The Container class contains pages: it
is at one level a collection class for Page
objects
"""
import logging
import urllib.request
import json
import spacy
from adam.graphable import Graphable
from adam.page import Page


class Container(Graphable):
    """
    The Container class.
    """
    def __initold__(self, manifest_json, nlp=None):
        super().__init__()
        self._manifest = manifest_json
        self._pages = []
        self._nlp = nlp

    def __init__(self, manifest_uri, nlp=None):
        super().__init__()
        self._manifest_uri = manifest_uri
        self._manifest = None
        self._pages = []
        self._nlp = nlp

    @property
    def manifest(self):
        """returns a manifest, loading it if necessary"""
        if not self._manifest:
            self.load_manifest()
        return self._manifest

    @property
    def nlp(self):
        """Returns a spaCy pipeline, creating it if it does not exist"""
        if not self._nlp:
            self._nlp = spacy.load("en_core_web_lg")
        return self._nlp

    @property
    def pages(self):
        """Returns the collection of Page objects,
           creating them if necessary"""
        if not self._pages:
            self.generate_pages()
        return self._pages

    def load_manifest(self):
        logging.info("downloading manifest")
        try:
            with urllib.request.urlopen(self._manifest_uri) as response:
                self._manifest = json.loads(response.read())
        except urllib.error.HTTPError as error:
            uri = self._manifest_uri
            msg = f"couldn't download from {uri}"
            logging.exception(msg, error)

    def generate_pages(self):
        """Iterates over page images and creates Page objects for each"""
        if "sequences" in self.manifest.keys():
            for canvas in self.manifest['sequences'][0]['canvases']:
                page = Page(canvas, self.nlp)
                self._pages.append(page)
        else:
            logging.debug("no sequences found")

    def build_graph(self):
        """
        Constructs a graph from all the pages.
        """
        graph = self.graph
        for page in self.pages:
            page.build_graph()
            graph += page.graph
