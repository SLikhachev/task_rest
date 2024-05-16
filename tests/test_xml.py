#import pytest

import os
from pathlib import Path
import pytest

@pytest.fixture
def envs():
    """ return xml endpoint parameters """

    test_year = os.getenv('TEST_YEAR') or '2021'
    test_month = os.getenv('TEST_MONTH') or '11'
    test_sign = os.getenv('TEST_SIGN') or False
    limit = os.getenv('TEST_LIMIT') or 0
    limit = int(limit)
    # return fresh dict for every test
    return {
       'month': f'{test_year}-{test_month}',
       'type': 'xml',
       'pack': 1,
       'limit': limit,
       'test': 0,
       'sent': 0,
       'fresh': 0,
       'sign': test_sign
    }


def test_create(app):
    """ Test application created """
    assert app.testing


def test_xml_check(client, envs):
    """ Test checks mode for xml endpoint """

    envs['test'] = 1
    resp = client.post('/reestr/xml/pack', data=envs)
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_xml_pack(client, envs):
    """ Test create mode for xml endpoint """

    resp = client.post('/reestr/xml/pack', data=envs)
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


def test_xml_errf(client):
    """ Test parsing Bars errors file POST request """

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
    """ Test download parsed Bars errors file GET request """

    resp = client.get('/reestr/xml/errf')
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')


