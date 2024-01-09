""" Integration test for a mek moving (the records in the DB table with the small int field calling MEK)
    The Moving is a process of:
    1. in one table - UPDATE a MONTH (small int) fields incrementally i.e. add 1,2, to the field (up to 12)
    2. between differnt tables - INSERT the MEK fields from one table to the next one
    WARNING !!!
    The tables names matter, they should be ended on the 2 year's digits i.e.
    if the current year is 2024 then the test tables should be:
    talonz_clin_23 - prev year
    talonz_clin_24 - curr year
    para_clin_23
    para_clin_24
    So, before the tests running you should correct the records in the DB_INIT_FILE appropriately
"""

import os
import pytest
import psycopg2
import psycopg2.extras


@pytest.fixture(scope='module')
def db():
    """ craete db connection object """
    #print(os.getcwd())
    db_uri = os.getenv('DB_URI')
    init_db_file = os.getenv('DB_INIT_FILE')
    assert db_uri, "For MEK tests we should set `mek_db=URI` config param"
    assert init_db_file, "For MEK tests we should set `init_mek_db_file=data/sql/mek_db.sql` config param"

    _db = psycopg2.connect(db_uri)
    # init DB tables

    with open(init_db_file, encoding='utf-8') as fd:
        _sql = fd.read()
    with _db.cursor() as curs:
        curs.execute(_sql)
        _db.commit()

    yield _db
    _db.commit()
    _db.close()


@pytest.fixture(scope='module')
def qurs(db):
    """ create cursor DB connection object """
    print("\n")
    _qurs = db.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    yield _qurs
    _qurs.close()


def test_create(app, qurs):
    """ Test application object created """
    assert app.testing, "No application object found"
    assert qurs, "No DB connection cursor supplied"


def test_dispatch_mek_request(client, qurs):
    """ Test the correctness of the dates fields and tables present
        Despite of the request method this checks made by dispatch method
        of the Mek class, so we use GET
    """
    # check No table exists
    resp = client.get('/reestr/inv/mek', data={
       'month': '2021-01',
       'target': '2021-02',
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    #
    rd = resp.get_json()
    assert not rd['done']
    assert 'Нет целевой таблицы talonz_clin' in rd['message']

    # check No records with MEK
    resp = client.get('/reestr/inv/mek', data={
       'month': '2023-10',
       'target': '2023-11',
    })
    assert resp.status_code == 200
    rd = resp.get_json()
    assert not rd['done']
    assert 'Нет записей с МЭК за месяц' in rd['message']

#
# Tests fot GET request
#

def test_copy_csv(client, qurs):
    """ Test copy MEK to csv file ../static/data/reestr/mek/file.csv
    """
    resp = client.get('/reestr/inv/mek', data={
       'month': '2023-11',
       'target': '2023-12',
    })
    assert resp.status_code == 200
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    print('\n')
    # should print
    # МЭК за месяц декабрь 2023, записей в файле 3", file: *.csv
    rd = resp.get_json()
    assert rd['file']
    assert rd['done']
    assert 'записей в файле' in rd['message']

#
# Test for POST request
#

def test_year(client, qurs):
    """ Test target year
    """
    # ---------- Test current year only
    resp = client.post('/reestr/inv/mek', data={
       'month': '2023-11',
       'target': '2023-12',
    })
    assert resp.status_code == 400
    assert resp.headers.get('Content-Type') == 'application/json'
    assert resp.headers.get('Access-Control-Allow-Origin') == '*'
    rd = resp.get_json()
    assert not rd['done']
    assert 'Переносить МЭК можно только на текущий год' in rd['message']

    # ----------- Test more than one year
    resp = client.post('/reestr/inv/mek', data={
       'month': '2022-11',
       'target': '2024-01',
    })
    assert resp.status_code == 400
    rd = resp.get_json()
    #print(rd)
    assert not rd['done']
    assert 'Переносить МЭК можно только на один год вперед' in rd['message']

    # ------------- Test from dec to jan
    resp = client.post('/reestr/inv/mek', data={
       'month': '2023-11',
       'target': '2024-01',
    })
    assert resp.status_code == 400
    rd = resp.get_json()
    #print(rd)
    assert not rd['done']
    assert 'можно только с декабря на январь' in rd['message']


def test_move_from_last_year(client, qurs):
    """ Test move fron last year
        Then we can test in current year conditions
    """
    resp = client.post('/reestr/inv/mek', data={
       'month': '2023-12',
       'target': '2024-01',
    })
    assert resp.status_code == 200
    rd = resp.get_json()
    #print(rd)
    assert rd['done']
    assert 'Пернесли МЭКи на Январь' in rd['message']
    qurs.execute('SELECT count(tal_num) FROM talonz_clin_24 WHERE talon_month=1 AND mek=1;')
    res = qurs.fetchone()
    assert res[0] == 2
    qurs.execute('SELECT count(id) FROM para_clin_24;')
    res = qurs.fetchone()
    assert res[0] == 2


def test_move_in_year(client, qurs):
    """ Test move mek in current year (same talonz table) """

    resp = client.post('/reestr/inv/mek', data={
       'month': '2024-01',
       'target': '2024-02',
    })
    assert resp.status_code == 200
    print('\n')
    rd = resp.get_json()
    assert 'Пернесли МЭКи на Февраль' in rd['message']
    qurs.execute('SELECT count(tal_num) FROM talonz_clin_24 WHERE talon_month=2 AND mek=1;')
    res = qurs.fetchone()
    assert res[0] == 2
