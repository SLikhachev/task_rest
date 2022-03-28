#import pytest
from pathlib import Path


def test_create(app):
    assert app.testing


def test_calc(client):
    resp = client.post('/reestr/inv/calc', data={
       'pack': 1,
       'smo': '25011',
       'month': '2021-11',
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
