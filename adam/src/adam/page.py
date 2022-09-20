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
from pathlib import Path, PosixPath
import logging
from types import NoneType
from numpy import newaxis
import requests
import pytesseract
import pandas as pd
import spacy
from rdflib import URIRef, Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from adam.global_vars import PAGE_IMAGE_CACHE
from adam.graphable import Graphable
from adam.named_entity import NamedEntity
from adam.manifest import Canvas


class Page(Graphable):
    def __init__(self, canvas_object: Canvas, metadata={}):
        super().__init__()
        self._canvas = canvas_object
        self.metadata = metadata
        self._nlp = None
        self._doc = None
        self._text = None
        self._entities = None
        self._confidence_threshold = 95

    @property
    def id(self):
        return self._canvas.id.split("/")[-1]

    @property
    def confidence_threshold(self) -> int:
        return self._confidence_threshold

    @confidence_threshold.setter
    def confidence_threshold(self, value: int):
        """Reset the confidence threshold.

        If the value is unchanged, do nothing. If
        it is different, update the threshold and
        reset the properties the depend on the text.
        """
        if self._confidence_threshold != value:
            self._confidence_threshold = value
            self.reset()

    @property
    def nlp(self):
        return self._nlp

    @nlp.setter
    def nlp(self, value):
        self._nlp = value
        self.reset()

    @property
    def text(self):
        if self._text is None:
            data_frame: pd.DataFrame = self._canvas.ocr_data
            data_frame = data_frame[data_frame.conf > self._confidence_threshold]
            data_frame = data_frame.reset_index().fillna("")
            words = []
            for _, token in data_frame.iterrows():
                if not (token.isnull()["text"]):
                    words.append(token["text"])
            self._text = " ".join(words).strip()
        return self._text

    @property
    def doc(self):
        if self._doc is None:
            self.do_nlp()
        return self._doc

    @property
    def entities(self):
        if self._entities is None:
            self._entities = [NamedEntity(ent) for ent in self.doc.ents]
        return self._entities

    @property
    def sentences(self):
        return list(self.doc.sents)

    def rendering(self, rendering_type):
        return [
            r["@id"] for r in self._canvas.renderings if r["format"] == rendering_type
        ]

    def do_nlp(self):
        if self._nlp is None:
            self._nlp = spacy.load("en_core_web_sm")
        self._doc = self._nlp(self.text)

    def reset(self):
        self._text = None
        self._doc = None
        self._entities = None

    def build_graph(self):
        for entity in self.entities:
            inscription_id = self.gen_id("inscription")
            self.graph.add(
                (inscription_id, RDF.type, self.namespace("ecrm")["E34_Inscription"])
            )

            self.graph.add((inscription_id, RDFS.label, Literal(entity.string)))

            self.graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["P128i_is_carried_by"],
                    URIRef(self._canvas.id),
                )
            )

            self.graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["P190_has_symbolic_content"],
                    Literal(entity.string),
                )
            )

            self.graph.add(
                (
                    inscription_id,
                    self.namespace("ecrm")["E55_Type"],
                    Literal(entity.type),
                )
            )

    def export_file_path(self, base_dir: Path, suffix: str) -> Path:
        return base_dir / Path(self.id).with_suffix(suffix)

    def export_as_jsonl(self, path: Path):
        fname = self.export_file_path(path, ".jsonl")
        with fname.open("w", encoding="utf-8", newline="\n") as f:
            for s in self.sentences:
                sentences = {}
                sentences["text"] = s.text
                sentences["meta"] = self.metadata
                json.dump(sentences, f, ensure_ascii=False)
                f.write("\n")

    def export_as_txt(self, path: Path):
        fname = self.export_file_path(path, ".txt")
        fname.write_text(self.text)

    def export_as_csv(self, path: Path):
        fname = self.export_file_path(path, ".csv")
        self._canvas.ocr_data.to_csv(fname)

    def export_as_rdf(self, path: Path):
        fname = self.export_file_path(path, ".ttl")
        self.build_graph()
        self.serialize(fname)
