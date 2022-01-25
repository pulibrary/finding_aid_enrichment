# -*- coding: utf-8 -*-

import os
import pytest
from adam.page import Page

testable_image = os.path.join(
    os.path.dirname(__file__),
    "testable_image.tif")


@pytest.fixture(name="basic_page")
def fixture_basic_page():
    """Returns empty page"""
    return Page(testable_image)


def test_text(basic_page):
    assert len(basic_page.text) > 0

def test_hocr(basic_page):
    assert len(basic_page.hocr) > 0

def test_alto(basic_page):
    assert len(basic_page.alto) > 0

def test_nlp(basic_page):
    assert "Acheson" in [token.text for token in basic_page.doc.ents]
