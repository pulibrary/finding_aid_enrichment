import requests
import json

manifest= 'https://figgy.princeton.edu/concern/scanned_resources/2a701cb1-33d4-4112-bf5d-65123e8aa8e7/manifest'

class ManifestLoader:
    """Loads a manifest into GraphDB via its
    rest interface."""

    def __init__(self, url, repository, server_url="http://localhost:7200"):
        self._base_url = server_url + "/rest/data/import/upload"
        self._data = {}
        self._headers = {}
        self._repository = repository
        self.set_default_headers()
        self.set_default_data()
        self._data['data'] = url
        self._data['name'] = url

    def set_default_headers(self):
        self._headers['Content-Type'] = 'application/ld+json'

    def set_default_data(self):
        self._data = {"replaceGraphs": [],
                      "baseURI": None,
                      "forceSerial": False,
                      "type": "url",
                      "format": "application/ld+json",
                      "parserSettings": {"preserveBNodeIds": False,
                                         "failOnUnknownDataTypes": False,
                                         "verifyDataTypeValues": False,
                                         "normalizeDataTypeValues": False,
                                         "failOnUnknownLanguageTags": False,
                                         "verifyLanguageTags": True,
                                         "normalizeLanguageTags": False,
                                         "stopOnError": True},
                      "requestIdHeadersToForward": None}

    @property
    def repository(self):
        return self._repository

    @repository.setter
    def repository(self, repository_id):
        self._repository = repository_id

    @property
    def url(self):
        if not self._repository:
            raise ValueError("no repository specified")
        return "/".join((self._base_url, self._repository, "url"))

    @property
    def data(self):
        return json.dumps(self._data)

    @property
    def headers(self):
        return self._headers

    def load(self):
        response = requests.post(self.url,
                                 headers=self.headers,
                                 data=self.data)
        return response

def load_ttl_file(path):
    headers = {"Content-Type": "application/x-turtle"}
    url = "http://localhost:7200/repositories/thunk/statements"

    with open(path, 'rb') as f:
        response = requests.post(url, headers=headers, data=f)
    return  response

file = "/Users/cwulfman/Desktop/correspondence_data/Box_1__Folder_1/Box_1__Folder_1.ttl"
