
PACK_TYPE=3
# create temp table statements
CREATE= 'CREATE TEMP TABLE'
_MO= 'invoice_mo'

# temp invioce's for MO table definition
INVOICE='''
(num int primary key,
fam varchar(32),
im varchar(32),
ot varchar(32),
pol char(1),
dr date
polis varchar (20),
open_date date,
close_date date,
ds varchar(8),
napr varchar(25),
napr_date date,
code_usl varchar(20),
sum_usl numeric(10,2)
);'''

VALS='''
 VALUES (
'{num}', '{fam}', '{im}', '{ot}', '{pol}', '{dr}',
'{polis}', '{open_date}', '{close_date}', '{ds}', '{napr}', '{napr_date}',
'{code_usl}', '{sum_usl}'
);
'''
# for MO self calculate (name is constatnt yet)
CREATE_INV_TBL= f'{CREATE} {_MO} {INVOICE}'
INSERT_INV_TBL= f'INSERT INTO {_MO} {VALS}'

GET_INV_ROW='''
SELECT
    tal.tal_num as num,
    crd.fam as fam,
    crd.im as im,
    crd.ot as ot,
    crd.gender as pol,
    crd.birth_date as dr,
    crd.polis_num as polis,
    tal.open_date as open_date,
    tal.close_date as close_date,
    tal.ds1 as ds,
    tal.naprlech as napr,
    tal.npr_date as napr_date,
    pmu.code_usl as code_usl,
    tar.tarif::numeric(10,2) as sum_usl
FROM
    talonz_clin_{year} as tal, --ch(2)
    cardz_clin as crd,
    para_clin_{year} as pmu,
    tarifs_pmu_vzaimoras as tar
WHERE
    tal.talon_month={month} AND -- int
    tal.npr_mo={mo_code} AND -- int
    tal.crd_num=crd.crd_num AND
    pmu.tal_num=tal.tal_num AND
    pmu.code_usl=tar.code AND
    {fresh};
'''

FRESH='tal.talon_type=1'
ALLTYPES='tal.talon_type > 0'

GET_MOS= '''
select
distinct tal.npr_mo as mo_code, mo.name as mo_name
from talonz_clin_{year} as tal, mo_local as mo
where talon_month={month} and mo.scode=tal.npr_mo;
'''

SET_SENT="update talonz_clin_{year} set talon_type=2 where tal_num={tal_num};"
