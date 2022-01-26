# -*- coding: utf-8 -*-
import os
import pytest
import spacy
from rdflib import Graph, Literal, Namespace, URIRef
from adam.page import Page, Graphable


test_canvas = {'@type': 'sc:Canvas', '@id': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266', 'label': '1', 'rendering': [{'@id': 'https://figgy.princeton.edu/downloads/84304756-8e12-4a21-aad1-ba6d67582266/file/45b6c33b-2b1c-4307-bb6c-a897e2a49e8c', 'label': 'Download the original file', 'format': 'image/tiff'}], 'width': 3774, 'height': 4770, 'images': [{'@type': 'oa:Annotation', 'motivation': 'sc:painting', 'resource': {'@type': 'dctypes:Image', '@id': 'https://iiif-cloud.princeton.edu/iiif/2/ad%2F7d%2F1b%2Fad7d1b2e62604a2aa1976ad8dbd21ba9%2Fintermediate_file/full/1000,/0/default.jpg', 'height': 4770, 'width': 3774, 'format': 'image/jpeg', 'service': {'@context': 'http://iiif.io/api/image/2/context.json', '@id': 'https://iiif-cloud.princeton.edu/iiif/2/ad%2F7d%2F1b%2Fad7d1b2e62604a2aa1976ad8dbd21ba9%2Fintermediate_file', 'profile': 'http://iiif.io/api/image/2/level2.json'}}, '@id': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/image/84304756-8e12-4a21-aad1-ba6d67582266', 'on': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266'}]}


spacy_nlp = spacy.load('en_core_web_sm')

@pytest.fixture(name="basic_page")
def fixture_basic_page():
    return Page(test_canvas, spacy_nlp)

def test_id(basic_page):
    assert type(basic_page.id) is URIRef
