import requests
from rdflib import Graph

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://localhost:7200/repositories/manifests")
sparql.setReturnFormat(JSON)

sparql.setQuery("""
prefix sc: <http://iiif.io/api/presentation/2#>
select distinct ?a where { 
	?s a sc:Canvas .
    ?s sc:hasImageAnnotations ?lst.
    ?lst rdf:first ?a
} limit 100 
""")

try:
    ret = sparql.queryAndConvert()

    for r in ret["results"]["bindings"]:
        print(r)
except Exception as e:
    print(e)
