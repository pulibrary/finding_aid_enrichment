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


class Container(Graphable):
    """
    The Container class.
    """

    def __init__(self, manifest_uri, nlp=None, cache_dir_root=None):
        super().__init__()
        self._manifest_uri = manifest_uri
        self._manifest = None
        self._pages = []
        self._nlp = nlp
        self._cache_dir_root = cache_dir_root

    @property
    def cache_dir(self):
        if self._cache_dir_root:
            return Path(self._cache_dir_root) / Path(self.container_label)
        else:
            return None

    @property
    def _id(self):
        """returns the uuid portion of the manifest @id"""
        return self.manifest['@id'].split('/')[-2]

    @property
    def metadata(self):
        """returns a dict of metadata from the manifest"""
        metadata = {}
        for item in self.manifest['metadata']:
            metadata[item['label']] = item['value']
        return metadata

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

    @property
    def container_label(self):
        if 'Container' in self.metadata.keys():
            string_label = self.metadata['Container'][0]
        else:
            string_label = self._id
        return re.sub(r"[,. ]", "_", string_label)

    def load_manifest(self):
        logging.info("downloading manifest |%s|" % self._manifest_uri)
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
                page = Page(canvas, self.nlp, self.metadata, self.cache_dir)
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

    def export(self, target_dir_name, fmt="txt"):
        target_dir = Path(target_dir_name) / Path(self.container_label)
        target_dir.mkdir(parents=True, exist_ok=True)
        for page in self.pages:
            file_name = str(page.id).rsplit('/', maxsplit=1)[-1] + '.' + fmt
            page.export(target_dir / file_name, fmt)

    def dump(self, target_dir_name):
        """
        Serializes the container in all formats:
        plain text, hocr, alto, and rdf
        """

        for fmt in ['txt', 'csv', 'jsonl']:
            logging.info("exporting format %s" % fmt)
            self.export(target_dir_name, fmt)

        target_dir = Path(target_dir_name) / Path(self.container_label)
        target_dir.mkdir(parents=True, exist_ok=True)
        self.build_graph()
        logging.info("serializing RDF")
        rdf_file_name = self.container_label + '.' + 'ttl'
        self.serialize(target_dir / rdf_file_name)
