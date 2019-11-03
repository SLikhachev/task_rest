
TYPE= (
    ('ambul', 'Амбулаторный', 'reestr_amb'),
    ('onko', 'Онкология', 'reestr_onk'),
    ('dsc', 'Дневной стационар', 'reestr_dsc'),
    ('prof', 'Профосмотр', 'reestr_pro'),
    ('foms', 'Инокраевые', 'reestr_foms'),
    ('pmu', 'Тарифы ПМУ', 'tarifs'),
)

FAIL= ('Неверный код МО', 'Тип счета не поддерживается', 'Нет записей в реестре')

SET_META= '''INSERT INTO invoice_meta( lpu, smo, yar, mon, typ )
VALUES ( %s, %s, %s, %s, %s );
'''
# INVOICE
'''
n_zap int primary key,
id_pac int,
spolis varchar(10),
npolis varchar(16),
usl_ok int,
vidpom int,
for_pom int,
date_z_1 date,
date_z_2 date,
rslt int,
ishod int,
profil int,
nhistory int,
ds1 varchar(6),
prvs int,
idsp int,
sumv numeric(11, 2),
sank_it numeric(11, 2),
fam varchar(32),
im varchar(32),
ot varchar(32),
w smallint,
dr date
'''

_MO= 'invoice_mo'
_BARS= 'invoice_bars'
_INS= 'INSERT INTO %s '
_INS_BARS=  _INS % _BARS
_INS_MO= _INS % _MO
_DATA_HM= '''(
    "n_zap", "id_pac", "spolis", "npolis",
    "usl_ok", "vidpom", "for_pom", "date_z_1", "date_z_2", "rslt", "ishod",
    "profil", "nhistory", "ds1", "prvs",
    "idsp", "sumv", "sank_it"
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s
)'''
_DATA_MO= '''(
    n_zap, id_pac, spolis, npolis,
    usl_ok, vidpom, for_pom, date_z_1, date_z_2, rslt, ishod,
    profil, nhistory, ds1, prvs,
    idsp, sumv, sank_it,
    fam, im, ot, w, dr
) VALUES (
    %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s, %s, %s
)'''

_TRUNC= 'TRUNCATE TABLE %s;'
TRUNC_INV_MO= _TRUNC % _MO
TRUNC_INV_BARS= _TRUNC % _BARS
INS_BARS= f'{_INS_BARS}{_DATA_HM}'
INS_MO= f'{_INS_MO}{_DATA_MO}'

#trunc_meta= 'TRUNCATE TABLE invoice_meta;
_COUNT= 'SELECT count(n_zap) FROM %s;'
COUNT_BARS= _COUNT % _BARS
COUNT_MO= _COUNT % _MO

PERSQ= 'UPDATE invoice_bars SET fam=%s, im=%s, ot=%s, w=%s, dr=%s WHERE id_pac=%s;'

_GET_ROW= 'SELECT * FROM %s ORDER BY nhistory;'
GET_ROW_BARS= _GET_ROW % _BARS
GET_ROW_MO= _GET_ROW % _MO

GET_MO_NAME= 'SELECT sname FROM mo_local WHERE scode=%s'
GET_SMO_NAME= 'SELECT name FROM smo_local WHERE code=%s'
STUB_MO= 'UNKNOWN MO NAME'
STUB_SMO= 'UNKNOWN SMO NAME'

GET_ROW_INV= 'SELECT nhistory FROM invoice_bars ORDER BY nhistory;'
GET_TALON= 'SELECT crd_num, smo FROM talonz_clin WHERE tal_num=%s;'
UPDATE_TAL_SMO= 'UPDATE talonz_clin SET smo=%s WHERE tal_num=%s;'
UPDATE_CRD_SMO= 'UPDATE cardz_clin SET smo=%s WHERE crd_num=%s;'