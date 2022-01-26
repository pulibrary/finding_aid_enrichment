# -*- coding: utf-8 -*-

import os
import json
import pytest
from adam.container import Container

testable_manifest_file = os.path.join(
    os.path.dirname(__file__),
    "testable_manifest.json")


@pytest.fixture(name="simple_container")
def fixture_simple_container():
    """Returns a container"""
    with open(testable_manifest_file) as file:
        manifest = json.load(file)
    return Container(manifest)

def test_pages(simple_container):
    assert len(simple_container.pages) == 11

def test_serialization(simple_container):
    outfile = "/tmp/foo.ttl"
    simple_container.build_graph()
    simple_container.serialize(outfile, 'ttl')
    assert(os.path.exists(outfile))

