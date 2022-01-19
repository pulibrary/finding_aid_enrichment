import json
from pathlib import Path
from rdflib import URIRef
from adam.container import Container

class PageText:
    def __init__(self, canvas, nlp, metadata, cachedir=None):
        super().__init__()
        self._canvas = canvas
        self.id = URIRef(self._canvas['@id'])
        self._file_path = cachedir / Path(str(self.id).rsplit('/')[-1] + '.txt')
        
        

base_path = Path("/Users/cwulfman/Desktop/correspondence_data")
manifest_path = Path('/Users/cwulfman/repos/github/pulibrary/finding_aid_enrichment/adam/tests') / Path('testable_manifest.json')

manifest_uri = "https://figgy.princeton.edu/concern/scanned_resources/44301149-e2e2-419d-9d7a-f89d8be9266d/manifest?manifest=https://figgy.princeton.edu/concern/scanned_resources/44301149-e2e2-419d-9d7a-f89d8be9266d/manifest"

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

container = Container(manifest_uri)

container_path = base_path / Path(container.container_label)

canvases = manifest['sequences'][0]['canvases']

page_text = PageText(canvases[0], None, None, container_path)

