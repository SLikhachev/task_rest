FILE_P = 'reestr_pro'

TYPE= (
    ('ambul', 'Амбулаторный', 'reestr_amb'),
    ('onko' 'Онкология', 'reestr_onk'),
    ('dsc', 'Дневной стационар', 'reestr_dsc'),
    ('foms', 'Инокраевые', 'reestr_foms'),
)

FAIL= ('Неверный код МО', 'Тип счета не поддерживается')

SET_META= '''INSERT INTO invoice_meta( lpu, smo, yar, mon, typ )
VALUES ( %s, %s, %s, %s, %s );
'''

GET_INV_ROW= 'SELECT * FROM invoice;'
GET_MO_NAME= 'SELECT sname FROM mo_local WHERE scode=%s'
GET_SMO_NAME= 'SELECT name FROM smo_local WHERE code=%s'
STUB_MO= 'UNKNOWN MO NAME'
STUB_SMO= 'UNKNOWN SMO NAME'