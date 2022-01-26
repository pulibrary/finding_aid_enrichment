"""The adam Page module

The Page module encapsulates OCR and NER.

  Typical usage:

  page = Page(path_to_image)
  page_text = page.text
  page_hocr = page.hocr
  page_alto = page.alto

Pages may be serialized as graphs of
entities.
"""

from sys import stdout

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import spacy
from rdflib import Graph, Literal, Namespace, URIRef, XSD
from rdflib.namespace import RDFS, RDF
import shortuuid
import urllib.request
import json


class Graphable:
    """ The Graphable class holds info about ontologies"""

    def __init__(self):
        """Initializes a Graphable. Sets up namespaces and establishes an id."""
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
        return self.namespace(ns)[shortuuid.uuid()]

    def build_graph(self):
        """Does nothing in the base class; intended to be implemented by each subclass"""
        pass

    def serialize(self, path=stdout, format='ttl'):
        self.graph.serialize(destination=path, format=format)


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
        

class Page(Graphable):
    """Encapsulates OCR and NER processes. """
    def __init__(self, canvas, spacy_pipeline=None):
        super().__init__()
        self._canvas = canvas
        # self._id = self.gen_id('page')
        self._id = URIRef(canvas['@id'])
        self._nlp = spacy_pipeline
        self._image_file = None
        self._text = False
        self._hocr = False
        self._alto = False
        self._doc = False
        self._entities = False


    @property
    def image_file(self):
        if not self._image_file:
            self.load_image()
        return self._image_file

    @property
    def text(self):
        if not self._text:
            self.do_ocr_to_string()
        return self._text

    @property
    def hocr(self):
        if not self._hocr:
            self.do_ocr_to_hocr()
        return self._hocr

    @property
    def alto(self):
        if not self._alto:
            self.do_ocr_to_alto()
        return self._alto

    @property
    def doc(self):
        if not self._doc:
            self.do_nlp()
        return self._doc

    @property
    def entities(self):
        if not self._entities:
            self._entities = [NamedEntity(ent) for ent in self.doc.ents]
        return self._entities

    @property
    def names(self):
        return [ent for ent in self.entities
                if ent.type == "PERSON"]


    def load_image(self):
        """ Download the rendering of the canvas"""

        image_uri = self._canvas['rendering'][0]['@id']
        fname = "/tmp/" + image_uri.split('/')[-1]
        urllib.request.urlretrieve(image_uri, fname)
        self._image_file = fname


    def do_ocr_to_string(self):
        self._text = pytesseract.image_to_string(Image.open(self.image_file))

    def do_ocr_to_hocr(self):
        self._hocr = pytesseract.image_to_pdf_or_hocr(
            Image.open(self.image_file), extension='hocr')

    def do_ocr_to_alto(self):
        self._alto = pytesseract.image_to_alto_xml(
            Image.open(self.image_file))

    def do_nlp(self):
        if not self._nlp:
            self._nlp = spacy.load('en_core_web_lg')
        self._doc = self._nlp(self.text)
        return self._doc

    def build_graph(self):
        """Constructs a graph of inscriptions on the page. The inscriptions
        are composed of the entities recognized by spaCy.

        inscriptionX a crm:E34_Inscription ;
                     crm:P106_is_composed_of entity.id ;
                     crm:P128i_is_carried_by self.id .
        """
        for entity in self.entities:
            g = self.graph
            ecrm = self.namespace('ecrm')
            g += entity.graph
            inscription_id = self.gen_id('inscription')
            self.graph.add((inscription_id,
                            RDF.type,
                            ecrm['E34_Inscription']))

            self.graph.add((inscription_id,
                            ecrm['P106_is_composed_of'],
                            entity.id
                            ))

            self.graph.add((inscription_id,
                            ecrm['P128i_is_carried_by'],
                            self.id))

            self.graph.add((inscription_id,
                            ecrm['E55_Type'],
                            self.namespace('etype')[entity.type]))
