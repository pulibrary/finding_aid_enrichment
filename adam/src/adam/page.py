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
import json
import re
import os
import logging
import urllib.request
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import pandas
import spacy
from rdflib import URIRef
from rdflib.namespace import RDF
from adam.graphable import Graphable
from adam.named_entity import NamedEntity


class Page(Graphable):
    """Encapsulates OCR and NER processes. """
    def __init__(self, canvas, spacy_pipeline=None, metadata={}):
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
        self.metadata = metadata

    @property
    def image_file(self):
        if not self._image_file:
            self.load_image()
        return self._image_file

    @property
    def text(self):
        if not self._text:
            self.do_get_text_string()
            self.clean_ocr_text()
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
    def sentences(self):
        return self.doc.sents

    @property
    def names(self):
        return [ent for ent in self.entities
                if ent.type == "PERSON"]

    def clean_ocr_text(self):
        """Stub for cleaning dirty ocr."""
        p = re.compile(r"\n")
        self._text = p.sub(' ', self._text)

    def file_path_of(self, image_uri):
        """Returns the path of the (cached) image"""
        return "/tmp/" + image_uri.split('/')[-1]

    def image_is_cached(self, image_path):
        return os.path.exists(image_path)

    def rendering(self, rendering_type):
        return [r['@id'] for r in self._canvas['rendering']
                      if r['format'] == rendering_type]

    def load_image(self):
        """
        Download the rendering of the canvas, if it
        hasn't already been downloaded.
        """
        image_renderings = [r['@id'] for r in self._canvas['rendering'] if r['format'] == 'image/tiff']
        image_uri = image_renderings[0]
        fname = self.file_path_of(image_uri)
        if not self.image_is_cached(fname):
            urllib.request.urlretrieve(image_uri, fname)
        self._image_file = fname

    def do_get_text_string(self):
        """
        (Disabling for now; using filtering version of
        do_ocr_to_string().)

        If OCR of the page already exists in Figgy, 
        use that; otherwise, download the image file
        and run ocr on it.
        """
        rendering_uri = self.rendering('text/plain')
        if rendering_uri:
            logging.info("there's a text/plain rendering in Figgy")
            with urllib.request.urlopen(rendering_uri[0]) as response:
                self._text = response.read().decode('utf-8')
        else:
            logging.info("doing our own ocr")
            self.do_ocr_to_string()

    def do_ocr_to_string(self):
        """
        Converts image to plain text string and stores
        it in self._text.

        Process the image with pytesseract into a Pandas data frame.
        Throw out blank lines; then group the text into blocks and filter
        out any block whose mean confidence score is below a threshold. 

        Using algorithms suggested in the following:
        - https://stackoverflow.com/questions/55406993/how-to-get-confidence-of-each-line-using-pytesseract
        - https://medium.com/geekculture/tesseract-ocr-understanding-the-contents-of-documents-beyond-their-text-a98704b7c655

        
        """
        df = pytesseract.image_to_data(Image.open(self.image_file),
                                               output_type='data.frame')
        # throw out blank lines
        text = df[df.conf != -1]
        blocks = text.groupby('block_num')['text'].apply(list)
        #print(text)
        blocks = blocks.reset_index()
        scores = text.groupby(['block_num'])['conf'].mean()
        data = []
        for i, r in blocks.iterrows():
            if scores[i+1] > 55:
                data.append(" ".join(r['text']))
                #return [' '.join(block) for block in data]
        self._text = " ".join(data)

    def do_ocr_to_string_simple(self):
        self._text = pytesseract.image_to_string(Image.open(self.image_file))

    def do_ocr_to_hocr(self):
        self._hocr = pytesseract.image_to_pdf_or_hocr(
            Image.open(self.image_file), extension='hocr').decode("utf-8")

    def do_ocr_to_alto(self):
        self._alto = pytesseract.image_to_alto_xml(
            Image.open(self.image_file)).decode("utf-8")

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

    def export(self, stream, format="text"):
        if format == "hocr":
            stream.write(self.hocr)
        elif format == 'alto':
            stream.write(self.alto)
        elif format == 'jsonl':
            for s in self.sentences:
                dict = {}
                dict['text'] = s.text
                dict['meta'] = self.metadata
                json.dump(dict, stream, ensure_ascii=False)
                stream.write("\n")
        else:
            stream.write(self.text)
