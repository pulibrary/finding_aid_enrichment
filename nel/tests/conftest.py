import os
import py
import pytest

_dir = os.path.dirname(os.path.realpath(__file__))
FIXTURE_DIR = py.path.local(_dir) / 'test_files'

@pytest.fixture()
def small_test():
    return os.path.join(FIXTURE_DIR, 'small-data.tsv')
