"""The adam Container module

The Container class contains pages: it
is at one level a collection class for Page
objects
"""
import re
from pathlib import Path
import logging
import urllib.request
import json
import spacy
from adam.page import Page
from adam.graphable import Graphable
from adam.manifest import Manifest


class Container(Graphable):
    """
    The Container Class
    """

    def __init__(self, manifest_object, nlp=None):
        super().__init__()
        self._manifest = manifest_object
        self._nlp = nlp
        self._pages = None

    @property
    def id(self):
        """returns the uuid portion of the manifest @id"""
        return self._manifest.id

    @property
    def metadata(self):
        """returns a dict of metadata from the manifest"""
        return self._manifest.metadata

    @property
    def pages(self):
        if self._pages is None:
            self.generate_pages()
        return self._pages

    @property
    def nlp(self):
        return self._nlp

    @nlp.setter
    def nlp(self, value):
        if self._nlp != value:
            self._nlp = value
            for page in self.pages:
                page.nlp = value

    @property
    def label(self):
        if "Container" in self._manifest.metadata.keys():
            string_label = self._manifest.metadata["Container"][0]
        else:
            string_label = self.id

        return re.sub(r"[,. ]", "_", string_label)

    def generate_pages(self):
        self._pages = [Page(canvas) for canvas in self._manifest.canvases]

    def dump(self, target_dir_name):
        """
        Serializes the container in all formats:
        plain text, hocr, alto, and rdf
        """
        base_dir = Path(target_dir_name) / Path(self.id)
        base_dir.mkdir(parents=True, exist_ok=True)
        for page in self.pages:
            page.export_as_txt(base_dir)
            page.export_as_csv(base_dir)
            page.export_as_jsonl(base_dir)
            page.export_as_rdf(base_dir)
