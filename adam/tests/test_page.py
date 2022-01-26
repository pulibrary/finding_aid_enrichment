# -*- coding: utf-8 -*-

import os
import pytest
import spacy
import json
from adam.page import Page

test_canvas = {'@type': 'sc:Canvas', '@id': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266', 'label': '1', 'rendering': [{'@id': 'https://figgy.princeton.edu/downloads/84304756-8e12-4a21-aad1-ba6d67582266/file/45b6c33b-2b1c-4307-bb6c-a897e2a49e8c', 'label': 'Download the original file', 'format': 'image/tiff'}], 'width': 3774, 'height': 4770, 'images': [{'@type': 'oa:Annotation', 'motivation': 'sc:painting', 'resource': {'@type': 'dctypes:Image', '@id': 'https://iiif-cloud.princeton.edu/iiif/2/ad%2F7d%2F1b%2Fad7d1b2e62604a2aa1976ad8dbd21ba9%2Fintermediate_file/full/1000,/0/default.jpg', 'height': 4770, 'width': 3774, 'format': 'image/jpeg', 'service': {'@context': 'http://iiif.io/api/image/2/context.json', '@id': 'https://iiif-cloud.princeton.edu/iiif/2/ad%2F7d%2F1b%2Fad7d1b2e62604a2aa1976ad8dbd21ba9%2Fintermediate_file', 'profile': 'http://iiif.io/api/image/2/level2.json'}}, '@id': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/image/84304756-8e12-4a21-aad1-ba6d67582266', 'on': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266'}]}

testable_image_old = os.path.join(
    os.path.dirname(__file__),
    "testable_images/3.tif")

testable_image = os.path.join(
    os.path.dirname(__file__),
    "testable_image.tif")

spacy_nlp = spacy.load('en_core_web_sm')


@pytest.fixture(name="basic_page")
def fixture_basic_page():
    return Page(test_canvas, spacy_nlp)

def test_text(basic_page):
    assert len(basic_page.text) > 0




def test_hocr(basic_page):
    assert len(basic_page.hocr) > 0

def test_alto(basic_page):
    assert len(basic_page.alto) > 0

def test_nlp(basic_page):
    assert "George Kennan Papers" in [token.text for token in basic_page.doc.ents]

def test_names(basic_page):
    assert len(basic_page.names) > 0

def test_entitites(basic_page):
    assert basic_page.entities[0].type == "PERSON"

def test_serialization(basic_page):
    outfile = "/tmp/foo.ttl"
    basic_page.build_graph()
    basic_page.serialize(outfile, 'ttl')
    assert(os.path.exists(outfile))

