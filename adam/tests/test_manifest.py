# -*- coding: utf-8 -*-

import os
import json
import pytest
from adam.manifest import Manifest, Canvas

manifest_1_url = "https://figgy.princeton.edu/concern/scanned_resources/3c782d03-59be-4d6c-b421-3cbf697f9447/manifest"


@pytest.fixture(name="manifest_1")
def fixture_manifest_1():
    """Returns a container"""
    return Manifest(manifest_1_url)


@pytest.fixture(name="canvas_1")
def canvas_1(manifest_1):
    return manifest_1.canvases[0]


def test_manifest_1(manifest_1):
    assert len(manifest_1.canvases) == 2
    assert manifest_1.label == "1922"
    assert manifest_1.id == "3c782d03-59be-4d6c-b421-3cbf697f9447"


def test_canvas(canvas_1):
    assert canvas_1.label == "Image00001.tif"
    assert (
        canvas_1.id
        == "https://figgy.princeton.edu/concern/scanned_resources/3c782d03-59be-4d6c-b421-3cbf697f9447/manifest/canvas/f8e8bf82-1496-424d-b053-d49dc82648af"
    )


def test_canvas_rendering(canvas_1):
    renderings = canvas_1.renderings
    assert len(renderings) == 2
    assert renderings[0]["format"] == "text/plain"
    assert renderings[1]["format"] == "image/tiff"
