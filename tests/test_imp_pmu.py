
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
def tarifs_file(test_data_path, tarifs_file_name):
    return test_data_path / 'tarifs' / tarifs_file_name

def test_app(init_app):
    """ Test application object created """
    assert init_app, "Application object does not inited"

def test_update_pmu(client, tarifs_file_name, tarifs_file):
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

def test_create_pmu(client, tarifs_file_name, tarifs_file):
    """ testing import pmu tarifs file """
    table = tarifs_file_name.split('.')[0]
    resp = client.post('/sprav/tarifs/update', data={
        'files': (open(tarifs_file, 'rb'), tarifs_file_name),
        'table': table,
        'copy': True
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}\n')