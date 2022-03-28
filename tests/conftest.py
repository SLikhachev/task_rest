import os
import sys
#import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def app():
    TEST_DIR = Path (sys.path[0])
    SITE_DIR= TEST_DIR.parent
    STATIC_DIR = SITE_DIR / 'static'

    sys.path.append(str(SITE_DIR))

    #print(sys.path)
    from poly import create_app
    app = create_app(SITE_DIR, STATIC_DIR)
    app.config.update({
        "TESTING": True,
    })

    yield app

    # clean up / reset resources here


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

