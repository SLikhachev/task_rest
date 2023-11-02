#import pytest

import os
from pathlib import Path


def test_create(app):
    assert app.testing


def test_xml_pack(client):
    test_year = os.getenv('TEST_YEAR') or '2021'
    test_month = os.getenv('TEST_MONTH') or '11'
    month = f'{test_year}-{test_month}'
    resp = client.post('/reestr/xml/pack', data={
       'mo_code': os.getenv('MO_CODE') or '250796',
       'month': month,
       'type': 'xml',
       'pack': 1,
       'test': 0,
       'sent': 0,
       'fresh': 0,
       'sign': 1
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_xml_errf(client):
    fname = os.getenv('BARS_ERR_FILE') or ''
    errf = Path(__file__).parent / 'data' / fname
    resp = client.post('/reestr/xml/errf', data={
        'ptype':1,
        'files': (open( errf, 'rb'), fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_xml_errf_csv(client):
    resp = client.get('/reestr/xml/errf')
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


