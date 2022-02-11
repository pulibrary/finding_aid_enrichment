"""
The NamedEntity class
"""

from rdflib import Literal
from rdflib.namespace import RDFS, RDF
from adam.graphable import Graphable


class NamedEntity(Graphable):
    """Holds data from spaCy"""
    def __init__(self, ent):
        super().__init__()
        self._id = self.gen_id('entity')
        self._string = ent.text
        self.type = ent.label_
        self.build_graph()

    def build_graph(self):
        """
        Constructs a graph that looks like this:

        id a ecrm:E90_Symbolic_Object;
           rdfs:label "Acheson";
           ecrm:P190_has_symbolic_content "Acheson" .
        """
        content = Literal(self._string)
        self.graph.add((self.id,
                        RDF.type,
                        self.namespace('ecrm')['E90_Symbolic_Object']))

        self.graph.add((self.id,
                        RDFS.label,
                        content))

        self.graph.add((self.id,
                        self.namespace('ecrm')['P190_has_symbolic_content'],
                        content))
