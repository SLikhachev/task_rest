
import os
import pytest
from pathlib import Path
import psycopg2
import psycopg2.extras


@pytest.fixture
def tarifs_file_name():
    file = os.getenv("TARIFS_CSV_FILE")
    assert file, "Should set `TARIFS_CSV_FILE` config param"
    return file

@pytest.fixture
def sql_init_file_name():
    file = os.getenv("DB_INIT_FILE")
    assert file, "Should set `DB_INIT_FILE` config param"
    return file

@pytest.fixture
def tarifs_file(test_data_path, tarifs_file_name):
    return test_data_path / 'tarifs' / tarifs_file_name

@pytest.fixture
def db_init_file(test_data_path, sql_init_file_name):
    return test_data_path / 'sql' / sql_init_file_name

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
def db(db_init_file):
    """ craete db connection object to test DB """
    #print(os.getcwd())
    db_uri = os.getenv('DB_URI')
    assert db_uri, "For TARIFS UPDATE tests we should set `DB_URI` config param"

    _db = psycopg2.connect(db_uri)
    # init DB tables
    with open(db_init_file, encoding='utf-8') as fd:
        assert fd, "DB_INIT_FILE not found"
        _sql = fd.read()

    with _db.cursor() as curs:
        curs.execute(_sql)
        _db.commit()

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


def test_create(app, qurs):
    """ Test application object created """
    assert app.testing, "Application object is not created"
    assert qurs, "DB connection cursor is not created"


def test_imp_pmu(client, tarifs_file_name, tarifs_file):
    """ testing import pmu tarifs file """
    table = tarifs_file_name.split('.')[0]
    resp = client.post('/sprav/tarifs/update', data={
        'files': (open(tarifs_file, 'rb'), tarifs_file_name),
        'table': table
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}\n')

