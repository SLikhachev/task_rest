
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
_INV= 'invoice_bars'
_USL= 'invoice_pmu'
_INS= 'INSERT INTO %s '
_INS_INV= _INS % _INV
_INS_MO= _INS % _MO
_INS_USL= _INS % _USL
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
_DATA_USL= '''(
    code_usl, kol_usl, tarif, profil, prvs
) VALUES (
    %s, %s, %s, %s, %s
)'''

_TRUNC= 'TRUNCATE TABLE %s;'
TRUNC_TBL_MO= _TRUNC % _MO
TRUNC_TBL_INV= _TRUNC % _INV
TRUNC_TBL_USL= _TRUNC % _USL

INS_INV= f'{_INS_INV}{_DATA_HM}'
INS_MO= f'{_INS_MO}{_DATA_MO}'
INS_USL= f'{_INS_USL}{_DATA_USL}'

#trunc_meta= 'TRUNCATE TABLE invoice_meta;
_COUNT= 'SELECT count(n_zap) FROM %s;'
COUNT_INV= _COUNT % _INV
COUNT_MO= _COUNT % _MO
COUNT_USL= 'SELECT count(code_usl) FROM %s' % _USL

PERSQ= 'UPDATE invoice_bars SET fam=%s, im=%s, ot=%s, w=%s, dr=%s WHERE id_pac=%s;'

_GET_ROW= 'SELECT * FROM %s ORDER BY nhistory;'
GET_ROW_INV= _GET_ROW % _INV
GET_ROW_MO= _GET_ROW % _MO

GET_MO_NAME= 'SELECT sname FROM mo_local WHERE scode=%s'
GET_SMO_NAME= 'SELECT name FROM smo_local WHERE code=%s'
STUB_MO= 'UNKNOWN MO NAME'
STUB_SMO= 'UNKNOWN SMO NAME'

GET_ROW_INV_TAL= 'SELECT nhistory FROM invoice_bars ORDER BY nhistory;'
GET_TALON= 'SELECT crd_num, smo FROM talonz_clin WHERE tal_num=%s;'
UPDATE_TAL_SMO= 'UPDATE talonz_clin SET smo=%s WHERE tal_num=%s;'
UPDATE_CRD_SMO= 'UPDATE cardz_clin SET smo=%s WHERE crd_num=%s;'

GET_USL= """
SELECT inv.code_usl, pmu.name, inv.kol_usl, inv.tarif 
FROM %s AS inv, pmu 
WHERE 
inv.code_usl=pmu.code_usl
ORDER BY inv.code_usl
""" % _USL
