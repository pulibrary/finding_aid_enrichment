"""
The Graphable Class
"""

from sys import stdout
from rdflib import Graph, Namespace
from shortuuid import uuid


class Graphable:
    """ The Graphable class holds info about ontologies"""

    def __init__(self):
        """Initializes a Graphable. 
        Sets up namespaces and establishes an id.
        """
        self._graph = Graph()
        self._namespaces = {
            "ecrm": Namespace("http://erlangen-crm.org/200717/"),
            "sc": Namespace("http://iiif.io/api/presentation/2#"),
            "page": Namespace("https://figgy.princeton.edu/concerns/pages/"),
            "entity": Namespace("https://figgy.princeton.edu/concerns/entities/"),
            "inscription": Namespace("https://figgy.princeton.edu/concerns/inscriptions/"),
            "etype": Namespace("https://figgy.princeton.edu/concerns/adam/")
        }

        manager = self._graph.namespace_manager

        for prefix, namespace in self._namespaces.items():
            manager.bind(prefix, namespace)

    @property
    def id(self):
        return self._id

    @property
    def graph(self):
        return self._graph

    def namespace(self, key):
        return self._namespaces[key]

    def gen_id(self, ns):
        return self.namespace(ns)[uuid()]

    def build_graph(self):
        """Does nothing in the base class; intended to be implemented by each subclass"""
        pass

    def serialize(self, path=stdout, fmt='ttl'):
        self.graph.serialize(destination=path, format=fmt)
