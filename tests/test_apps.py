#import pytest
from pathlib import Path


def test_create(app):
    assert app.testing

