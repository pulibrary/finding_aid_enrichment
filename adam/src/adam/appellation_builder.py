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

import sys
from pathlib import Path
import csv
import argparse
from sys import stdout
import logging


path = "/Users/cwulfman/Downloads/freq-20-15-csv.tsv"

appellations = {}

with open(path, 'r') as data_file:
    reader = csv.DictReader(data_file, delimiter='\t')
    for row in reader:
        appellation = row['appellation']
        if appellation not in appellations.keys():
            appellations[appellation] = {}
            appellations[appellation]['viaf_id'] = row['VIAF_ID']
            appellations[appellation]['inscriptions'] = []

        appellations[appellation]['inscriptions'].append(row['inscription'])
        
