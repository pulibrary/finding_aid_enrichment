"""
The Graphable Class
"""

import pathlib
from sys import stdout
from typing import Union, IO, TextIO
from rdflib import Graph, Namespace
from shortuuid import uuid


class Graphable:
    """The Graphable class holds info about ontologies"""

    def __init__(self):
        """Initializes a Graphable.
        Sets up namespaces and establishes an id.
        """
        self._graph = None
        self._namespaces = {
            "ecrm": Namespace("http://erlangen-crm.org/200717/"),
            "sc": Namespace("http://iiif.io/api/presentation/2#"),
            "page": Namespace("https://figgy.princeton.edu/concerns/pages/"),
            "actor": Namespace("https://figgy.princeton.edu/concerns/actors/"),
            "appellation": Namespace(
                "https://figgy.princeton.edu/concerns/appellations/"
            ),
            "entity": Namespace("https://figgy.princeton.edu/concerns/entities/"),
            "inscription": Namespace(
                "https://figgy.princeton.edu/concerns/inscriptions/"
            ),
            "etype": Namespace("https://figgy.princeton.edu/concerns/adam/"),
        }

    # @property
    # def graph_id(self):
    #     return self._id

    @property
    def graph(self):
        if self._graph is None:
            self._graph = Graph()
            manager = self._graph.namespace_manager

            for prefix, namespace in self._namespaces.items():
                manager.bind(prefix, namespace)

            self.build_graph()
        return self._graph

    def namespace(self, key):
        return self._namespaces[key]

    def gen_id(self, ns):
        return self.namespace(ns)[uuid()]

    def build_graph(self):
        """Does nothing in the base class; intended to be implemented by each subclass"""
        pass

    def serialize(
        self, path: Union[str, pathlib.PurePath, IO[bytes]], fmt: str = "ttl"
    ):
        self.graph.serialize(destination=path, format=fmt)
