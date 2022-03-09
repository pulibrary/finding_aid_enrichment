# -*- coding: utf-8 -*-

import os
import pytest
import spacy
from rdflib import URIRef
from adam.page import Page

test_canvas = {'@type': 'sc:Canvas', '@id': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266', 'label': '1', 'rendering': [{'@id': 'https://figgy.princeton.edu/downloads/84304756-8e12-4a21-aad1-ba6d67582266/file/45b6c33b-2b1c-4307-bb6c-a897e2a49e8c', 'label': 'Download the original file', 'format': 'image/tiff'}], 'width': 3774, 'height': 4770, 'images': [{'@type': 'oa:Annotation', 'motivation': 'sc:painting', 'resource': {'@type': 'dctypes:Image', '@id': 'https://iiif-cloud.princeton.edu/iiif/2/ad%2F7d%2F1b%2Fad7d1b2e62604a2aa1976ad8dbd21ba9%2Fintermediate_file/full/1000,/0/default.jpg', 'height': 4770, 'width': 3774, 'format': 'image/jpeg', 'service': {'@context': 'http://iiif.io/api/image/2/context.json', '@id': 'https://iiif-cloud.princeton.edu/iiif/2/ad%2F7d%2F1b%2Fad7d1b2e62604a2aa1976ad8dbd21ba9%2Fintermediate_file', 'profile': 'http://iiif.io/api/image/2/level2.json'}}, '@id': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/image/84304756-8e12-4a21-aad1-ba6d67582266', 'on': 'https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266'}]}

test_canvas_2 = {
          "@type": "sc:Canvas",
          "@id": "https://figgy.princeton.edu/concern/scanned_resources/721988d9-ab93-4b2d-b245-5a1667e8803c/manifest/canvas/f5167834-9307-4e5f-acfa-0f4cdf8dde4e",
          "label": "Image00001.tif",
          "rendering": [
            {
              "@id": "https://figgy.princeton.edu/concern/file_sets/f5167834-9307-4e5f-acfa-0f4cdf8dde4e/text",
              "format": "text/plain",
              "label": "Download page text"
            },
            {
              "@id": "https://figgy.princeton.edu/downloads/f5167834-9307-4e5f-acfa-0f4cdf8dde4e/file/a2743d1c-52fc-4d28-879d-b28e479cd962",
              "label": "Download the original file",
              "format": "image/tiff"
            }
          ],
          "width": 4066,
          "height": 6135,
          "images": [
            {
              "@type": "oa:Annotation",
              "motivation": "sc:painting",
              "resource": {
                "@type": "dctypes:Image",
                "@id": "https://iiif-cloud.princeton.edu/iiif/2/bc%2F00%2F5c%2Fbc005cb41b184e3d859397da1f86c908%2Fintermediate_file/full/1000,/0/default.jpg",
                "height": 6135,
                "width": 4066,
                "format": "image/jpeg",
                "service": {
                  "@context": "http://iiif.io/api/image/2/context.json",
                  "@id": "https://iiif-cloud.princeton.edu/iiif/2/bc%2F00%2F5c%2Fbc005cb41b184e3d859397da1f86c908%2Fintermediate_file",
                  "profile": "http://iiif.io/api/image/2/level2.json"
                }
              },
              "@id": "https://figgy.princeton.edu/concern/scanned_resources/721988d9-ab93-4b2d-b245-5a1667e8803c/manifest/image/f5167834-9307-4e5f-acfa-0f4cdf8dde4e",
              "on": "https://figgy.princeton.edu/concern/scanned_resources/721988d9-ab93-4b2d-b245-5a1667e8803c/manifest/canvas/f5167834-9307-4e5f-acfa-0f4cdf8dde4e"
            }
          ]
        }


@pytest.fixture(name="basic_page")
def fixture_basic_page():
    return Page(test_canvas,
                spacy.load('en_core_web_sm'),
                {'Container': ['Box 53, Folder 18 to 19']})

@pytest.fixture(name="page_with_ocr")
def fixture_ocr_page():
    return Page(test_canvas_2, spacy.load('en_core_web_sm'))

def test_id(basic_page):
    assert basic_page.id == URIRef('https://figgy.princeton.edu/concern/scanned_resources/6a83801b-9169-40a4-8ca7-1494c94727b9/manifest/canvas/84304756-8e12-4a21-aad1-ba6d67582266')

def test_metadata(basic_page):
    assert basic_page.metadata['Container'][0] == 'Box 53, Folder 18 to 19'

# def test_text(basic_page):
#     assert len(basic_page.text) > 0

# def test_hocr(basic_page):
#     assert len(basic_page.hocr) > 0

# def test_alto(basic_page):
#     assert len(basic_page.alto) > 0

# def test_nlp(basic_page):
#     assert "George Kennan Papers" in [token.text for token in basic_page.doc.ents]

# def test_names(basic_page):
#     assert len(basic_page.names) > 0

# def test_entitites(basic_page):
#     assert basic_page.entities[0].type == "PERSON"

# def test_serialization(basic_page):
#     outfile = "/tmp/foo.ttl"
#     basic_page.build_graph()
#     basic_page.serialize(outfile, 'ttl')
#     assert(os.path.exists(outfile))

def test_rendering(page_with_ocr):
    assert page_with_ocr.rendering('image/tiff')
    assert page_with_ocr.rendering('text/plain')
    assert not page_with_ocr.rendering('text/foo')

def test_get_rendering(page_with_ocr):
    assert page_with_ocr.text ==  "Kennan Papers (MC #076) Box 53 Folder 18 1957"
