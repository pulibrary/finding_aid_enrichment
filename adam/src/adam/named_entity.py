"""
The NamedEntity class
"""

from rdflib import Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from adam.graphable import Graphable


class NamedEntity(Graphable):
    """Holds data from spaCy"""

    def __init__(self, ent):
        super().__init__()
        self._id = self.gen_id("appellation")
        self.string = ent.text
        self.type = ent.label_
        self.build_graph()

    def __repr__(self) -> str:
        return f"{self.type}({self.string})"

    def build_graph(self):
        """
        Constructs a graph that looks like this:

        id a ecrm:E90_Symbolic_Object;
           rdfs:label "Acheson";
           ecrm:P190_has_symbolic_content "Acheson" .
        """
        content = Literal(self.string)
        self.graph.add((self._id, RDF.type, self.namespace("ecrm")["E41_Appellation"]))

        self.graph.add(
            (
                self._id,
                self.namespace("ecrm")["E55_Type"],
                self.namespace("etype")[self.type],
            )
        )

        self.graph.add((self._id, RDFS.label, content))

        self.graph.add(
            (self._id, self.namespace("ecrm")["P190_has_symbolic_content"], content)
        )
