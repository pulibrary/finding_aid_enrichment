# -*- coding: utf-8 -*-

import os
import json
import pytest
from adam.container import Container

testable_manifest_file = os.path.join(
    os.path.dirname(__file__),
    "testable_manifest.json")

testable_manifest_url = "https://figgy.princeton.edu/concern/scanned_resources/3c782d03-59be-4d6c-b421-3cbf697f9447/manifest"

@pytest.fixture(name="simple_container")
def fixture_simple_container():
    """Returns a container"""
    return Container(testable_manifest_url)

def test_id(simple_container):
    assert simple_container.id == '3c782d03-59be-4d6c-b421-3cbf697f9447'

def test_pages(simple_container):
    assert len(simple_container.pages) == 2

def test_serialization(simple_container):
    outfile = "/tmp/foo.ttl"
    simple_container.build_graph()
    simple_container.serialize(outfile, 'ttl')
    assert(os.path.exists(outfile))
