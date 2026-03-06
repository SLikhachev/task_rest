#import pytest
import os
from pathlib import Path


def test_create(app):
    assert app.testing


def test_onyear_fail(client):
    resp = client.post('/reestr/inv/onyear', data={
       'year': 2022,
    })
    assert resp.status_code == 400
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_onyear_ok(client):
    year = os.getenv('TEST_YEAR') or '2025'
    resp = client.post('/reestr/inv/onyear', data={
       'month': f'{year}-01',
       'onyear': False,
       'closed': True
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')

def test_onyear_month(client):
    year = os.getenv('TEST_YEAR') or '2025'
    resp = client.post('/reestr/inv/onyear', data={
       'month': f'{year}-01',
       'onyear': False,
       'closed': False
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
