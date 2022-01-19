# -*- coding: utf-8 -*-
import pytest
import spacy
from rdflib import Graph, URIRef
from adam.page import NamedEntity


spacy_nlp = spacy.load('en_core_web_sm')

doc = spacy_nlp("Fred Flintstone and Barney Rubble played golf.")


@pytest.fixture(name="simple_named_entity")
def fixture_simple_named_entity():
    """Returns a simple NamedEntity for testing"""
    return NamedEntity(doc.ents[0])

def test_id(simple_named_entity):
    assert type(simple_named_entity.id) is URIRef

def test_graph(simple_named_entity):
    assert type(simple_named_entity.graph) is Graph
