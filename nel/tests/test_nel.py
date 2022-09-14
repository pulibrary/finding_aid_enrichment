import csv
import pytest


def test(small_test):
    with open(small_test, 'r') as f:
        reader = csv.DictReader(f, )
        records = list(reader)
    assert len(records) == 2
