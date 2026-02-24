import os
import sys
#import tempfile
from pathlib import Path
import psycopg2
import psycopg2.extras
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


@pytest.fixture
def test_data_path() -> Path:
    return Path(__file__).parent / 'data'

# TODO create db if absent
"""
CREATE DATABASE omslite_test
  WITH
  ENCODING = 'UTF8'
  LC_COLLATE = 'ru_RU.UTF-8'
  LC_CTYPE = ' ru_RU.UTF-8'
  TEMPLATE = template0;
"""
@pytest.fixture()
def db():
    """ craete db connection object to test DB """
    #print(os.getcwd())
    db_uri = os.getenv('DB_URI')
    assert db_uri, "For TARIFS UPDATE tests we should set `DB_URI` config param"
    _db = psycopg2.connect(db_uri)
    yield _db
    _db.commit()
    _db.close()

@pytest.fixture()
def qurs(db):
    """ create cursor DB connection object """
    print("\n")
    _qurs = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    yield _qurs
    _qurs.close()

@pytest.fixture
def sql_init_file_name():
    file = os.getenv("DB_INIT_FILE")
    assert file, "Should set `DB_INIT_FILE` config param"
    return file

@pytest.fixture
def db_init_file(test_data_path, sql_init_file_name):
    return test_data_path / 'sql' / sql_init_file_name

@pytest.fixture()
def init_app(app, db_init_file, db, qurs):
    """ Test application object created """
    assert app.testing, "Application object is not created"
    assert qurs, "DB connection cursor is not created"

    with open(db_init_file, encoding='utf-8') as fd:
        assert fd, "DB_INIT_FILE not found"
        _sql = fd.read()

        qurs.execute(_sql)
        db.commit()
        return True