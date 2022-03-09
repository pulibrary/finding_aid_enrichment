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
import requests
# import urllib.request
import cv2
import pytesseract
import pandas
import spacy
from shutil import copyfileobj
from rdflib import URIRef
from rdflib.namespace import RDF
from adam.global_vars import PAGE_IMAGE_CACHE
from adam.graphable import Graphable
from adam.named_entity import NamedEntity


def file_path_of(image_uri):
    """Returns the path of the (cached) image"""
    return PAGE_IMAGE_CACHE / image_uri.split('/')[-1]

def image_is_cached(image_uri):
    """returns  does image exist in cache?"""
    return os.path.exists(PAGE_IMAGE_CACHE / image_uri.split('/')[-1])


class Page(Graphable):
    """Encapsulates OCR and NER processes. """
    def __init__(self, canvas, spacy_pipeline=None, metadata={}):
        super().__init__()
        self._canvas = canvas
        # self._id = self.gen_id('page')
        # self._id = URIRef(canvas['@id'])
        self._nlp = spacy_pipeline
        self._image_file = None
        self._image = None
        self._text = False
        self._hocr = False
        self._alto = False
        self._doc = False
        self._entities = False
        self.metadata = metadata

    @property
    def id(self):
        return URIRef(self._canvas['@id'])

    @property
    def image_path(self):
        return PAGE_IMAGE_CACHE / self.image_uri.split('/')[-1]

    @property
    def image(self):
        if not self._image:
            self._image = cv2.imread(str(self.image_file))
        return self._image

    @property
    def image_file(self):
        if not os.path.exists(self.image_path):
            self.download_image()
        return self.image_path

    @property
    def image_uri(self):
        image_renderings = [r['@id'] for r in
                            self._canvas['rendering']
                            if r['format'] == 'image/tiff']
        return image_renderings[0]
        

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


    def download_image(self):
        response = requests.get(self.image_uri, stream=True)
        if response.status_code == 200:
            response.raw.decode_content = True
            with open(self.image_path, 'wb') as f:
                copyfileobj(response.raw, f)
        else:
            print(f"couldn't download image file at {self.image_path}")

    def do_get_text_string(self, use_figgy=False):
        """
        (Disabling for now; using filtering version of
        do_ocr_to_string().)

        If OCR of the page already exists in Figgy, 
        use that; otherwise, download the image file
        and run ocr on it.
        """
        if use_figgy:
            rendering_uri = self.rendering('text/plain')
            if rendering_uri:
                logging.info("there's a text/plain rendering in Figgy")
                response = requests.get(rendering_uri[0])
                if response.status_code == 200:
                    self._text = response.text
                else:
                    logging.info("couldn't download image file")
        else:
            logging.info("doing our own ocr")
            self.do_ocr_to_string()

    def do_ocr_to_string(self, conf=95):
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
#        import pdb; pdb.set_trace()

        df = pytesseract.image_to_data(self.image, output_type='data.frame')
        df = df[df.conf > conf]
        print(f"df size=|{df.size}|")
        df = df.reset_index()
        df.fillna("", inplace=True)
        self._text = " ".join([r['text'] for _,r in df.iterrows()])

    def do_ocr_to_string_simple(self):
        self._text = pytesseract.image_to_string(self.image)

    def do_ocr_to_hocr(self):
        self._hocr = pytesseract.image_to_pdf_or_hocr(self.image, extension='hocr').decode("utf-8")

    def do_ocr_to_alto(self):
        self._alto = pytesseract.image_to_alto_xml(self.image).decode("utf-8")

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

    def export(self, file_path, format="txt"):
        if format == "hocr":
            with open(file_path, "w", encoding="utf-8") as stream:
                stream.write(self.hocr)
        elif format == 'alto':
            with open(file_path, "w", encoding="utf-8") as stream:
                stream.write(self.alto)
        elif format == 'jsonl':
            with open(file_path, "w", encoding="utf-8") as stream:
                for s in self.sentences:
                    sentences = {}
                    sentences['text'] = s.text
                    sentences['meta'] = self.metadata
                    json.dump(sentences, stream, ensure_ascii=False)
                    stream.write("\n")
        elif format == 'rdf':
            self.build_graph()
            self.serialize(file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as stream:
                stream.write(self.text)
