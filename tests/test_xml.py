#import pytest
from pathlib import Path


def test_create(app):
    assert app.testing


def test_xml_pack(client):
    resp = client.post('/reestr/xml/pack', data={
       'mo_code': '250796',
       'month': '2021-11',
       'type': 'xml',
       'pack': 1,
       'test': 0,
       'sent': 0,
       'fresh': 0
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_xml_errf(client):
    fname = 'FHT25M250796_21117962.xml'
    errf = Path(__file__).parent / 'files' / fname
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


