import os
import pytest
from pathlib import Path


@pytest.fixture
def fname():
    return os.getenv('BARS_INVOICE_FILE') or ''

@pytest.fixture
def invf(fname):
    return Path(__file__).parent / 'files' / fname


def test_create(app):
    assert app.testing


def test_inv_imp_app(client, invf, fname):
    """ testing import ambulance invoice file """

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


def test_inv_imp_usl(client, invf, fname):
    """ testing import ambulance invoice file as USL table """

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


def test_inv_imp_foms(client, invf, fname):
    """ testing import ambulance invoice file for TFOMS """

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


