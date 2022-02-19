"""
The Collection class.
"""
import json
import urllib.request
import logging
import spacy
from adam.graphable import Graphable
from adam.container import Container


class Collection(Graphable):
    """ The Collection Class. """

    def __init__(self, manifest_json, nlp=None):
        super().__init__()
        self._nlp = nlp
        self._manifest = manifest_json
        self._containers = None

    @property
    def manifest(self):
        """ returns the manifiest """
        return self._manifest

    @property
    def nlp(self):
        """Returns a spaCy pipeline, creating it if it does not exist"""
        if not self._nlp:
            self._nlp = spacy.load("en_core_web_lg")
        return self._nlp

    @property
    def containers(self):
        """
        returns the Containers in the collection,
        creating them if necessary.
        """
        if not self._containers:
            self._containers = []
            print("generating containers")
            for manifest in self.manifest['manifests']:
                manifest_url = manifest['@id']
                try:
                    response = urllib.request.urlopen(manifest_url)
                except urllib.error.HTTPError as e:
                    logging.error("url problem")
                    print(e.code)
                else:
                    print("loading response")
                    container_manifest = json.loads(response.read())
                    self._containers.append(Container(container_manifest, self.nlp))
        return self._containers

    def build_graph(self):
        """
        Constructs graph from all the containers.
        """
        graph = self.graph
        for container in self.containers:
            container.build_graph()
            graph += container.graph
