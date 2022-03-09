# global.py
from pathlib import Path

PAGE_IMAGE_CACHE = Path("/tmp/page_images")
PAGE_IMAGE_CACHE.mkdir(parents=True, exist_ok=True)
