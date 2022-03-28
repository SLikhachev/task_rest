#import pytest
from pathlib import Path


def test_create(app):
    assert app.testing


def test_inv_imp_app(client):

    fname = 'HM250796S25011_22027963.zip'
    invf = Path(__file__).parent / 'files' / fname
    resp = client.post('/reestr/inv/impex', data={
        'pack':1,
        'files': (open(invf, 'rb'), fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_inv_imp_usl(client):

    fname = 'HM250796S25011_22027963.zip'
    invf = Path(__file__).parent / 'files' / fname
    resp = client.post('/reestr/inv/impex', data={
        'pack':6,
        'files': (open(invf, 'rb'), fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_inv_imp_foms(client):

    fname = 'HM250796T25_22027961.zip'
    invf = Path(__file__).parent / 'files' / fname
    resp = client.post('/reestr/inv/impex', data={
        'pack':1,
        'files': (open(invf, 'rb'), fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


