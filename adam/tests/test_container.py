# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
import pytest
from adam.manifest import Manifest

from adam.container import Container, Page

testable_manifest_file = os.path.join(
    os.path.dirname(__file__), "testable_manifest.json"
)

testable_manifest_url = "https://figgy.princeton.edu/concern/scanned_resources/3c782d03-59be-4d6c-b421-3cbf697f9447/manifest"


@pytest.fixture(name="simple_container")
def fixture_simple_container():
    """Returns a container"""
    return Container(Manifest(testable_manifest_url))


def test_id(simple_container):
    assert simple_container.id == "3c782d03-59be-4d6c-b421-3cbf697f9447"


def test_pages(simple_container):
    assert len(simple_container.pages) == 2


def test_export(simple_container, tmp_path):
    simple_container.build_graph()
    base_dir = tmp_path / "test_container"
    base_dir.mkdir(parents=True, exist_ok=True)
    simple_container.dump(base_dir)
    assert base_dir.exists
    for p in simple_container.pages:
        for suffix in (".txt", ".jsonl", ".csv", ".ttl"):
            assert p.export_file_path(base_dir, suffix).exists
