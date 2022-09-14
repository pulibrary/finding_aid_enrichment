"""
The Appellation class


In this version, appellations are generated from data
that has been processed in OpenRefine.
"""

from rdflib import Literal
from rdflib.namespace import RDFS, RDF
from adam.graphable import Graphable


class Appellation(Graphable):
    def __init__(self, label, viaf_id=None, inscriptions=[]):
        super().__init__()
        self._id = self.gen_id('appellation')
        self.label = label
        self.viaf_id = viaf_id
        self.inscriptions = inscriptions
        self.build_graph()

    def build_graph(self):
        """
        Constructs a graph that looks like this:

        id a ecrm:E41_Appellation ;
           rdfs:label "Acheson" .

        id ecrm:P62i_is_depicted_by <inscription> .
        """
        label = Literal(self.label)
        self.graph.add((self.id,
                        RDF.type,
                        self.namespace('ecrm')['E41_Appellation']))

        self.graph.add((self.id,
                        RDFS.label,
                        label))

        for inscription in self.inscriptions:
            self.graph.add((self.id,
                            self.namespace('ecrm')['P62i_is_depicted_by'],
                            Literal(inscription)))
