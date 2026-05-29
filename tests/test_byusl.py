#import pytest
import os
import pytest
from pathlib import Path
from datetime import date

@pytest.fixture
def year():
    return os.getenv('TEST_YEAR') or date.today().year

def test_create(app):
    assert app.testing


def _test_byusl_fail(client):
    resp = client.post('/reestr/inv/byusl', data={
       'month': f'2012-01-01',
    })
    assert resp.status_code == 400
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')

def _test_byusl_month(client, year):
    resp = client.post('/reestr/inv/byusl', data={
       'month': f'{year}-01-01',
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def _test_byusl_period(client):
    resp = client.post('/reestr/inv/byusl', data={
        'date_beg': '2026-01-01',
        'date_end': '2026-02-11',
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')

def _test_byusl_year(client, year):
    resp = client.post('/reestr/inv/byusl', data={
        'month': f'{year}-01-01',
        'onyear': True
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_byusl_period_mo(client):
    resp = client.post('/reestr/inv/byusl', data={
        'date_beg': '2026-01-01',
        'date_end': '2026-02-11',
        'talons_mo': 747
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')