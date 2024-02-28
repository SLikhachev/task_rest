
import os
import pytest
from pathlib import Path
import psycopg2
import psycopg2.extras


@pytest.fixture
def csv_fname():
    return os.getenv('PMU_CSV_FILE') or ''

@pytest.fixture
def csv_invf(csv_fname):
    return Path(__file__).parent / 'data' / 'tarif' / csv_fname

@pytest.fixture(scope='module')
def db():
    """ craete db connection object """
    #print(os.getcwd())
    test_db = os.getenv('TEST_DB')
    if test_db:
        db_uri=test_db
    else:
        db_uri = os.getenv('DB_URI')
    init_db_file = os.getenv('DB_INIT_FILE')
    assert db_uri, "For TARIFS UPDATE tests we should set `DB_URI` config param"
    assert init_db_file, "For TRAIFS UPDATE tests we should set `DB_INIT_FILE` config param"

    _db = psycopg2.connect(db_uri)
    # init DB tables

    #test_db = os.getenv('TEST_DB')
    if test_db:
        with open(init_db_file, encoding='utf-8') as fd:
            _sql = fd.read()
        with _db.cursor() as curs:
            curs.execute(_sql)
            _db.commit()

    yield _db
    _db.commit()
    _db.close()


@pytest.fixture(scope='module')
def qurs(db):
    """ create cursor DB connection object """
    print("\n")
    _qurs = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    yield _qurs
    _qurs.close()


def test_create(app, qurs):
    """ Test application object created """
    assert app.testing, "No application object found"
    assert qurs, "No DB connection cursor supplied"


def test_imp_pmu(client, csv_invf, csv_fname):
    """ testing import pmu tarifs file """

    resp = client.post('/sprav/tarif/pmu', data={
        'files': (open(csv_invf, 'rb'), csv_fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}\n')

