#import pytest

def test_create(app):
    assert app.testing

def test_task(client):
    resp = client.get('/test?param=task')
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')

def test_rdbm(client):
    resp = client.get('/test?param=rdbm')
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    for k, v in resp.get_json().items():
        print(f'{k}: {v}')
