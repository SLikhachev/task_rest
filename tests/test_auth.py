
import os
import datetime
import jwt
import pytest


def encode(role, user, expired, secret):
    return jwt.encode(
        {
         "role": role,
         "user": user,
         'exp': expired
         },
        secret,
        algorithm="HS256"
    )

def wrong_encode(role, expired, secret):
    return jwt.encode(
        {
         "role": role,
         'exp': expired
         },
        secret,
        algorithm="HS256"
    )

@pytest.fixture
def role():
    return os.getenv('DB_ROLE')

@pytest.fixture
def user():
    return os.getenv('DB_CUSER')

@pytest.fixture
def expired():
    return datetime.datetime.now() - datetime.timedelta(hours=48)

@pytest.fixture
def valid():
    return datetime.datetime.now() + datetime.timedelta(minutes=15)

@pytest.fixture
def secret():
    return os.getenv('JWT_TOKEN_SECRET')

@pytest.fixture
def token_expired(role, user, expired, secret):
    return encode(role, user, expired, secret)

@pytest.fixture
def token_invalid(role, user, valid):
    return encode(role, user, valid, 'FDGKjhklnliojqwekokklijygjbqkjebkbkqexb')

@pytest.fixture
def wrong_payload(role, valid, secret):
    return wrong_encode(role, valid, secret)

@pytest.fixture
def token(role, user, valid, secret):
    return encode(role, user, valid, secret)

@pytest.fixture
def month():
    _y = os.getenv('TEST_YEAR') or '2021'
    _m = os.getenv('TEST_MONTH') or '11'
    return f'{_y}-{_m}'

@pytest.fixture
def data(month):
    return {
       'mo_code': os.getenv('MO_CODE') or '250796',
       'month': month,
       'type': 'xml',
       'pack': 1,
       'test': 0,
       'sent': 0,
       'fresh': 0
    }

@pytest.fixture
def url():
    return '/reestr/xml/pack'

def ok_hdr(token):
    return {'Authorization' : f'Bearer {token}'}

def bad_hdr(token):
    return {'Authorization' : f'{token}'}

#========= tests ============


def test_options(client, url):
    resp = client.options(url)
    assert resp.status_code == 200
    assert resp.headers.get('Access-Control-Allow-Methods') == 'OPTIONS,  GET,  POST'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    assert resp.headers.get('Access-Control-Allow-Headers') == 'Authorization'


def test_bad_hdr(client, url, token, data):
    resp = client.post(
        url,
        headers=bad_hdr(token),
        data=data
    )
    assert resp.status_code == 401
    assert b'Bad Authorization Bearer' in resp.data
    print(f'\n {str(resp.data, "UTF-8")} \n')


def test_invalid_token(client, url, token_invalid, data):
    resp = client.post(
        url,
        headers=ok_hdr(token_invalid),
        data=data
    )
    assert resp.status_code == 401
    assert b'Invalid token' in resp.data
    print(f'\n {str(resp.data, "UTF-8")}\n')


def test_expired_token(client, url, token_expired, data):
    resp = client.post(
        url,
        headers=ok_hdr(token_expired),
        data=data
    )
    assert resp.status_code == 401
    assert b'Token has expired' in resp.data
    print(f'\n {str(resp.data, "UTF-8")}\n')


def test_wrong_payload(client, url, wrong_payload, data):
    resp = client.post(
        url,
        headers=ok_hdr(wrong_payload),
        data=data
    )
    assert resp.status_code == 401
    assert b'Token payload invalid' in resp.data
    print(f'\n {str(resp.data, "UTF-8")}\n')


def test_no_auth(client, url, token, data):
    """ Test no auth, then pack will be made as
        DB_USER connections settings configured
        So all records will be selected
    """
    print('\n----------start no auth-----------------\n')
    os.environ['DB_AUTH']='no'
    resp = client.post(
        url,
        headers=ok_hdr(token),
        data=data
    )
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
    print('\n----------end no auth-----------------\n')

def test_auth_kola(client, url, token, data):
    """ Test auth, then pack will be made as
        DB_USER connections settings configured
        And only current user records will be selected
    """
    print('\n----------start kola-----------------\n')
    os.environ['DB_AUTH']='yes'
    resp = client.post(
        url,
        headers=ok_hdr(token),
        data=data
    )
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
    print('\n------------end kola-----------------\n')

