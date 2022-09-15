# The adam Page module

"""
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
import os
from shutil import copyfileobj
from pathlib import Path
import logging
import requests
import pytesseract
import pandas as pd
import spacy
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, RDFS
from adam.global_vars import PAGE_IMAGE_CACHE
from adam.graphable import Graphable
from adam.named_entity import NamedEntity


class Page(Graphable):
    """Encapsulates OCR and NER processes. """
    def __init__(self, canvas, spacy_pipeline=None, metadata={}, cache_dir=None):
        super().__init__()
        self._canvas = canvas
        self._nlp = spacy_pipeline
        self._image_file = None
        self._doc = False
        self._entities = False
        self._ocr_data = False
        self._text = ""
        self.ocr_processed = False
        self.metadata = metadata
        self.cache_dir = None
        if cache_dir:
            self.cache_dir = Path(cache_dir)

    @property
    def id(self):
        return URIRef(self._canvas['@id'])

    @property
    def image_path(self):
        return PAGE_IMAGE_CACHE / self.image_uri.split('/')[-1]

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
    def ocr_data(self):
        """Use pytesseract to perform OCR and generate a
        pandas data frame. """
        if self.cache_dir:
            file_name = str(self.id).rsplit('/', maxsplit=1)[-1] + '.csv'
            self._ocr_data = pd.read_csv(self.cache_dir / Path(file_name))
            self.ocr_processed = True
        if not self.ocr_processed:
            self._ocr_data = pytesseract.image_to_data(
                str(self.image_file),
                output_type='data.frame'
            )
            self.ocr_processed = True
        return self._ocr_data

    @property
    def text(self):
        """Constructs text string by concatenating all
        the text blocks in the ocr data frame."""

        if not self._text:
            if self.cache_dir:
                file_name = str(self.id).rsplit('/', maxsplit=1)[-1] + '.txt'
                with open(self.cache_dir / Path(file_name), 'r') as f:
                    self._text = f.read()
            else:
                data_frame = self.ocr_data.fillna("")
                self._text = " ".join([r['text'] for _, r in data_frame.iterrows()]).strip()
        return self._text

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

    def rendering(self, rendering_type):
        return [r['@id'] for r in self._canvas['rendering']
                if r['format'] == rendering_type]

    def download_image(self):
        logging.info("downloading image")
        try:
            response = requests.get(self.image_uri, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        response.raw.decode_content = True
        try:
            image_file = self.image_path.open("wb")
            copyfileobj(response.raw, image_file)
        except OSError as e:
            logging.exception(e)
        finally:
            image_file.close()

    def filtered_text(self, threshold=95):
        """Returns string composed only of text
        blocks with confidence scores higher
        than threshold.


        Process the image with pytesseract into a Pandas data frame.
        Throw out blank lines; then group the text into blocks and filter
        out any block whose mean confidence score is below a threshold.

        Using algorithms suggested in the following:
        - https://stackoverflow.com/questions/55406993/how-to-get-confidence-of-each-line-using-pytesseract
        - https://medium.com/geekculture/tesseract-ocr-understanding-the-contents-of-documents-beyond-their-text-a98704b7c655
        """

        data = self.ocr_data
        data = data[data.conf > threshold]
        data = data.reset_index()
        data = data.fillna("")
        return " ".join([r['text'] for _, r in data.iterrows()]).strip()

    def do_nlp(self):
        if not self._nlp:
            self._nlp = spacy.load('en_core_web_lg')
        self._doc = self._nlp(self.filtered_text())
        return self._doc

    def build_graph(self):
        g = self.graph
        for entity in self.entities:
            inscription_id = self.gen_id('inscription')
            self.graph.add((inscription_id,
                            RDF.type,
                            self.namespace('ecrm')['E34_Inscription']))

            self.graph.add((inscription_id,
                            RDFS.label,
                            Literal(entity._string)))

            self.graph.add((inscription_id,
                            self.namespace('ecrm')['P128i_is_carried_by'],
                            self.id))

            self.graph.add((inscription_id,
                            self.namespace('ecrm')['P190_has_symbolic_content'],
                            Literal(entity._string)))

            self.graph.add((inscription_id,
                            self.namespace('ecrm')['E55_Type'],
                            Literal(entity.type)))


    def build_graph_old(self):
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

    def export(self, file_path, format="txt"):
        if format == 'jsonl':
            with open(file_path, "w", encoding="utf-8") as stream:
                for s in self.sentences:
                    sentences = {}
                    sentences['text'] = s.text
                    sentences['meta'] = self.metadata
                    json.dump(sentences, stream, ensure_ascii=False)
                    stream.write("\n")
        elif format == 'csv':
            self.ocr_data.to_csv(file_path)
        elif format == 'rdf':
            self.build_graph()
            self.serialize(file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as stream:
                stream.write(self.text)
