# AppellationBuilder

"""
A quick-and-dirty script for processing an OpenRefine-generated
table of data into some RDF.

The table has the following fields:
content
appellation
VIAF_ID
page
title
container
image
manifest
canvas
inscription
"""

import re
import sys
from pathlib import Path
import csv
import argparse
from sys import stdout
import logging
from adam.appellation import Appellation


path = "/Users/cwulfman/Desktop/ColdWarPapers/MC076/openrefine_data_A-D.csv"


appellations = {}

with open(path, 'r') as data_file:
    reader = csv.DictReader(data_file)
    records = list(reader)
    
for row in records:
    if 'appellation' in row:
        appellation = row['appellation']
        if appellation not in appellations.keys():
            appellations[appellation] = {}
            appellations[appellation]['viaf_id'] = row['VIAF_ID']
            appellations[appellation]['inscriptions'] = []
        appellations[appellation]['inscriptions'].append(row['inscription'])
            
objects = []
for k in appellations.keys():
    viaf_id = appellations[k]['viaf_id']
    inscriptions = appellations[k]['inscriptions']
    objects.append(Appellation(k, viaf_id, inscriptions))

for o in objects:
    o.build_graph()
    fname = re.sub('[. ]', '', o.label)
    o.serialize('/tmp/output/' + fname + '.ttl')
