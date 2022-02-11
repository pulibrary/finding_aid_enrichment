"""The adam Container module

The Container class contains pages: it
is at one level a collection class for Page
objects
"""
import spacy
from adam.graphable import Graphable
from adam.page import Page


class Container(Graphable):
    """
    The Container class.
    """
    def __init__(self, manifest_json, nlp=None):
        super().__init__()
        self._manifest = manifest_json
        self._pages = []
        self._nlp = nlp

    @property
    def manifest(self):
        """returns a manifest, loading it if necessary"""
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

    def generate_pages(self):
        """Iterates over page images and creates Page objects for each"""
        for canvas in self.manifest['sequences'][0]['canvases']:
            page = Page(canvas, self.nlp)
            self._pages.append(page)

    def build_graph(self):
        """
        Constructs a graph from all the pages.
        """
        graph = self.graph
        for page in self.pages:
            page.build_graph()
            graph += page.graph
