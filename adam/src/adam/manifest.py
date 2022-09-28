"""The Manifest model

An object wrapper around IIIF manifest
objects.  Its primary purpose is to
cache image files.
"""
import json
import logging
import os
from shutil import copyfileobj
from pathlib import Path
import requests
import pandas as pd
import pytesseract

log = logging.getLogger(__name__)

manifest_uri = "https://figgy.princeton.edu/concern/scanned_resources/a3b5a622-8608-4a05-91cb-bc3840a44ef9/manifest"


class Manifest:
    """The Manifest class"""

    def __init__(self, manifest_uri):
        log.debug("downloading manifest |%s|" % manifest_uri)

        r = requests.get(manifest_uri)
        self.manifest = r.json()

        self._canvases = None

    @property
    def id(self):
        """returns the uuid portion of the manifest @id"""
        return self.manifest["@id"].split("/")[-2]

    @property
    def canvases(self):
        if self._canvases is None:
            self._canvases = []
            for canvas in self.manifest["sequences"][0]["canvases"]:
                self._canvases.append(Canvas(canvas))
        return self._canvases

    @property
    def label(self) -> str:
        return self.manifest["label"][0]

    @property
    def metadata(self):
        """returns a dict of metadata from the manifest"""
        metadata = {}
        for item in self.manifest["metadata"]:
            metadata[item["label"]] = item["value"]
        return metadata

    def __repr__(self) -> str:
        return f"Manifest({self.label})"

    def download_images(self):
        for canvas in self.canvases:
            canvas.download_image()


class Canvas:
    """The Canvas class"""

    page_image_cache = Path("/usr/local/var/cache/adam/images")
    page_ocr_cache = Path("/usr/local/var/cache/adam/ocr")

    def __init__(self, canvas_json):
        self.canvas = canvas_json
        self._ocr_data = None

    @property
    def id(self) -> str:
        return self.canvas["@id"]

    @property
    def label(self) -> str:
        return self.canvas["label"]

    def __repr__(self) -> str:
        return f"Canvas({self.label})"

    @property
    def renderings(self) -> list:
        return self.canvas["rendering"]

    @property
    def rendering(self, rendering_type):
        return [
            rendering
            for rendering in self.renderings
            if rendering["format"] == "image/tiff"
        ][0]["@id"]

    @property
    def image_uri(self):
        return [
            rendering
            for rendering in self.renderings
            if rendering["format"] == "image/tiff"
        ][0]["@id"]

    @property
    def image_uri_old(self):
        image_renderings = [
            r["@id"] for r in self.canvas["rendering"] if r["format"] == "image/tiff"
        ]
        return image_renderings[0]

    @property
    def image_path(self) -> Path:
        return self.page_image_cache / self.image_uri.split("/")[-1]

    @property
    def ocr_data_path(self) -> Path:
        return self.page_ocr_cache / self.image_uri.split("/")[-1]

    @property
    def image_file(self) -> Path:
        if not self.image_path.is_file():
            log.debug(f"image not cached")
            self.download_image()
        return self.image_path

    @property
    def ocr_data(self) -> pd.DataFrame:
        if self._ocr_data is None:
            if not self.ocr_data_path.is_file():
                log.debug(f"ocr not cached")
                self.perform_ocr()
            self._ocr_data = pd.read_csv(self.ocr_data_path)
        return self._ocr_data

    @property
    def ocr_data_old(self):
        if not self.ocr_data_path.is_file():
            log.debug(f"ocr not cached")
            self.perform_ocr()
        return self.ocr_data_path

    def download_image(self):
        log.debug(f"downloading {self.image_path}")
        try:
            response = requests.get(self.image_uri, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        response.raw.decode_content = True
        try:
            image_file = self.image_path.open("wb")
            copyfileobj(response.raw, image_file)
            image_file.close()
        except OSError as e:
            log.exception(e)

    def perform_ocr(self):
        ocr_data = pytesseract.image_to_data(
            str(self.image_file), output_type="data.frame"
        )
        ocr_data.to_csv(self.ocr_data_path)
