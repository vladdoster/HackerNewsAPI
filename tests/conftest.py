import sys
from os import path

import httpretty
import pytest

from hn import HN, Story
from hn import constants

PRESETS_DIR = path.join(path.dirname(__file__), 'presets')


def get_content(file):
    with open(path.join(PRESETS_DIR, file)) as f:
        return f.read()
