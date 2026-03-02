#import pytest
import os
from pathlib import Path


def test_create(app):
    assert app.testing


def test_formos(client):
    test_year = os.getenv('TEST_YEAR') or '2026'
    test_month = os.getenv('TEST_MONTH') or '01'
    month = f'{test_year}-{test_month}'
    resp = client.post('/reestr/inv/formo', data={
       'month': month,
       'sent': True,
       'fresh': False
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
