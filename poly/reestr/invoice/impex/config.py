

# names for output XLSX files with reestr data
TYPE= (
    ('ambul', 'Амбулаторный', 'reestr_amb'),
    ('onko', 'Онкология', 'reestr_onk'),
    ('dsc', 'Дневной стационар', 'reestr_dsc'),
    ('prof', 'Профосмотр', 'reestr_pro'),
    ('foms', 'Инокраевые', 'reestr_foms'),
    ('pmu', 'Тарифы ПМУ', 'tarifs'),
)

FAIL= ('Неверный код МО', 'Тип счета не поддерживается', 'Нет записей в реестре')

# stale, not used
SET_META= '''INSERT INTO invoice_meta( lpu, smo, yar, mon, typ )
VALUES ( %s, %s, %s, %s, %s );
'''
ERRORS_TABLE_NAME= 'None'

# temp invioce's table name definition
INVOICE='''
(n_zap int primary key,
id_pac int,
spolis varchar(10),
npolis varchar(16),
enp varchar(16),
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
sump numeric(11, 2),
fam varchar(32),
im varchar(32),
ot varchar(32),
w smallint,
dr date
)'''

# temp usl's table definition
USL='''
(code_usl character varying(20) NOT NULL primary key,
kol_usl integer,
tarif numeric(10,2),
profil integer,
prvs integer
)'''

# table name for MO self calculation invoice
_MO= 'invoice_mo'

# table name for invoice imported from BARS
_INV= 'invoice_bars'

# table name for invoice imported from BARS as USL
_USL= 'invoice_pmu'

# insert statement start
_INS= 'INSERT INTO'

# insert into invoice;s table
_INS_INV= f'{_INS} {_INV}'
_INS_MO= f'{_INS} {_MO}'
_INS_USL= f'{_INS} {_USL}'

# insert data definition to invoice table
_DATA_HM= '''(
    "n_zap", "id_pac", "spolis", "npolis", "enp",
    "usl_ok", "vidpom", "for_pom", "date_z_1", "date_z_2", "rslt", "ishod",
    "profil", "nhistory", "ds1", "prvs",
    "idsp", "sumv", "sump"
) VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s
)'''

# insert data definition to self calculated MO table
_DATA_MO= '''(
    n_zap, id_pac, spolis, npolis, enp,
    usl_ok, vidpom, for_pom, date_z_1, date_z_2, rslt, ishod,
    profil, nhistory, ds1, prvs,
    idsp, sumv, sump,
    fam, im, ot, w, dr
) VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s, %s, %s
)'''

# insert data definition to USL calculate table
_DATA_USL= '''(
    code_usl, kol_usl, tarif, profil, prvs
) VALUES (
    %s, %s, %s, %s, %s
)'''

# truncate table statemments
_TRUNC= 'DELETE FROM %s WHERE true;'
TRUNC_TBL_MO= _TRUNC % _MO
TRUNC_TBL_INV= _TRUNC % _INV
TRUNC_TBL_USL= _TRUNC % _USL

# create temp table statements
_CREATE= 'CREATE TEMP TABLE'
# for MO self calculate (name is constatnt yet)
CREATE_TBL_MO= f'{_CREATE} {_MO} {INVOICE}'

# for impoted from BARS invoice (random name)
CREATE_TBL_INV= f'{_CREATE} {{}} {INVOICE}'
CREATE_TBL_USL=  f'{_CREATE} {{}} {USL}'

# insert statements for persistent and temp table
INS_INV= f'{_INS_INV}{_DATA_HM}'
INS_INV_TMP = f'{_INS} {{}} {_DATA_HM}'

INS_MO= f'{_INS_MO}{_DATA_MO}'
INS_MO_TMP = f'{_INS} {{}} {_DATA_MO}'

INS_USL= f'{_INS_USL}{_DATA_USL}'
INS_USL_TMP= f'{_INS} {{}} {_DATA_USL}'

# stale stmnt, not used
#trunc_meta= 'TRUNCATE TABLE invoice_meta;

# count number of records in table
_COUNT_ZAP= 'SELECT count(n_zap) FROM'

# for BARS invoice
COUNT_INV= f'{_COUNT_ZAP} {_INV};'
COUNT_INV_TMP=f'{_COUNT_ZAP} {{}};'

# for self MO
COUNT_MO= f'{_COUNT_ZAP} {_MO};'

# count number of records in USL table
_COUNT_USL= f'SELECT count(code_usl) FROM'
COUNT_USL= f'{_COUNT_USL} {_USL};'
COUNT_USL_TMP= f'{_COUNT_USL} {{}};'

# insert personal data to invioce table
_PERSQ = 'SET fam=%s, im=%s, ot=%s, w=%s, dr=%s WHERE id_pac=%s;'
PERSQ= f'UPDATE invoice_bars {_PERSQ}'
PERSQ_TMP = f'UPDATE {{}} {_PERSQ}'

# select all records from invoice table
_GET_ROW= 'SELECT * FROM %s ORDER BY nhistory;'
GET_ROW_INV= _GET_ROW % _INV
GET_ROW_INV_TMP= _GET_ROW % '{}'
GET_ROW_MO= _GET_ROW % _MO

# select MO name from local MOs
GET_MO_NAME= 'SELECT sname FROM mo_local WHERE scode=%s'

# select SMO name from local SMOs
GET_SMO_NAME= 'SELECT name FROM smo_local WHERE code=%s'

# names for MO/SMO which not were find in local refs
STUB_MO= 'UNKNOWN MO NAME'
STUB_SMO= 'UNKNOWN SMO NAME'

# made for smo correction, not used yet
GET_ROW_INV_TAL= 'SELECT nhistory FROM invoice_bars ORDER BY nhistory;'
GET_SMO= '''
SELECT tal.crd_num, crd.smo FROM talonz_clin_%s AS tal, cardz_clin AS crd WHERE tal.tal_num=
'''
AND_CRD= ' AND crd.crd_num= tal.crd_num;'
UPDATE_TAL_SMO= 'UPDATE talonz_clin_%s SET smo=%s WHERE tal_num=%s;'
UPDATE_CRD_SMO= 'UPDATE cardz_clin SET smo=%s WHERE crd_num=%s;'

# select USL names by its CODE_USL
_GET_USL= """
SELECT inv.code_usl, pmu.name, inv.kol_usl, inv.tarif
FROM %s AS inv, pmu
WHERE
inv.code_usl=pmu.code_usl
ORDER BY inv.code_usl
"""
GET_USL = _GET_USL % _USL
GET_USL_TMP = _GET_USL % '{}'

# select
GET_INV_SMO='''
SELECT
t.crd_num, t.tal_num
FROM
talonz_clin_%s AS t,
cardz_clin AS c,
invoice_bars AS i
WHERE
t.tal_num = i.nhistory AND
t.crd_num = c.crd_num AND
-- t.talon_month=%s AND
c.smo <> %s;
 '''

# define talonz table for set MEK flag
GET_MEK_TABLE= '''
SELECT table_name FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema','pg_catalog') AND
table_name='talonz_clin_%s';
'''

# select talon_nums which will not been paid (MEK)
_MEK = 'SELECT nhistory FROM %s WHERE sump = 0.00;'
GET_MEK= _MEK % _INV
GET_MEK_TMP= _MEK % '{}'

# update talonz's records flagged as MEK
SET_MEK= 'UPDATE talonz_clin_%s SET mek=1, talon_type=1 WHERE tal_num='