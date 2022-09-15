import os
import pytest
from pathlib import Path


@pytest.fixture
def smo_fname():
    return os.getenv('BARS_SMO_INVOICE_FILE') or ''

@pytest.fixture
def smo_invf(smo_fname):
    return Path(__file__).parent / 'data' / smo_fname


def test_create(app):
    assert app.testing


def test_inv_imp_smo(client, smo_invf, smo_fname):
    """ testing import ambulance invoice file """

    resp = client.post('/reestr/inv/impex', data={
        'pack':1,
        'files': (open(smo_invf, 'rb'), smo_fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_inv_imp_usl(client, smo_invf, smo_fname):
    """ testing import ambulance invoice file as USL table """

    resp = client.post('/reestr/inv/impex', data={
        'pack':6,
        'files': (open(smo_invf, 'rb'), smo_fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_inv_imp_foms(client):
    """ testing import ambulance invoice file for TFOMS """

    _fname = os.getenv('BARS_FOMS_INVOICE_FILE') or ''
    fname = Path(__file__).parent / 'data' / _fname

    resp = client.post('/reestr/inv/impex', data={
        'pack':5,
        'files': (open(fname, 'rb'), _fname)
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


