
import os
import pytest
from pathlib import Path
import psycopg2
import psycopg2.extras

@pytest.fixture
def sql_init_file_name():
    #file = os.getenv("DB_INIT_FILE")
    #assert file, "Should set `DB_INIT_FILE` config param"
    #return file
    return 'drop_talonz_26.sql'

@pytest.fixture
def db_init_file(test_data_path, sql_init_file_name):
    return test_data_path / 'sql' / sql_init_file_name

def test_craete_app(app, db_init_file, db, qurs):
    """ Test application object created """
    assert app.testing, "Application object is not created"
    assert qurs, "DB connection cursor is not created"

    with open(db_init_file, encoding='utf-8') as fd:
        assert fd, "DB_INIT_FILE not found"
        _sql = fd.read()

        qurs.execute(_sql)
        db.commit()

def test_create_tal_table(client):
    """ testing import pmu tarifs file """
    resp = client.post('/clinic/talons/add_table')
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}\n')

