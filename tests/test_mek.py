#import pytest
from pathlib import Path


def test_create(app):
    assert app.testing


def test_mek(client):
    resp = client.post('/reestr/inv/mek', data={
       'month': '2022-01',
       'target': '2022-02',
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
