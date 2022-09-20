"""Create named entities from data file"""
import os
import csv

# data_file = "/Users/cwulfman/repos/github/pulibrary/finding_aid_enrichment/nel/tests/test_files/small-data.tsv"

path = "/Users/cwulfman/Desktop/ColdWarPapers/MC076/openrefine_data_A-D.csv"


appellations = {}

with open(path, "r") as data_file:
    reader = csv.DictReader(data_file)
    for row in reader:
        appellation = row["appellation"]
        if appellation not in appellations.keys():
            appellations[appellation] = {}
            appellations[appellation]["viaf_id"] = row["VIAF_ID"]
            appellations[appellation]["inscriptions"] = []
        appellations[appellation]["inscriptions"].append(row["inscription"])


# with open(data_file, 'r') as f:
#     reader = csv.DictReader(f)
#     records = list(reader)
