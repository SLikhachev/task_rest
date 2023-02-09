PROF= (21, 22)
STOM= (85, 86, 87, 88, 89, 90)
SESTRY= (82, 83)


GET_SMO_AMBUL = '''
SELECT
    tal.tal_num AS n_zap,
    tal.tal_num AS nhistory,
    tal.usl_ok,
    tal.mek,
    -- tal.vidpom,
    tal.for_pom,
    tal.open_date as date_z_1,
    tal.close_date as date_z_2,
    tal.purp,
    tal.rslt,
    tal.ishod,
    spec.profil,
    spec.prvs,
    tal.ds1,
    tal.visit_pol,
    tal.visit_home,
    tal.visit_homstac,
    tal.visit_daystac,
    tal.npr_mo,
    tal.ksg,
    -- idsp int,
    --crd.crd_num AS id_pac,
    crd.id AS id_pac,
    crd.smo,
    -- sumv numeric(11, 2),
    crd.fam,
    crd.im,
    crd.ot,
    crd.gender as w,
    crd.birth_date AS dr,
    crd.polis_ser AS spolis,
    crd.polis_num AS npolis
FROM
    talonz_clin_%s AS tal, cardz_clin AS crd,
    spec_prvs_profil as spec
WHERE
    tal.talon_type > 0 AND
    tal.talon_month=%s AND
    tal.usl_ok=3 AND
    crd.crd_num=tal.crd_num AND
    spec.spec=tal.doc_spec
ORDER BY tal.tal_num;
'''

SMO = 'crd.smo=%s AND'

GET_TALON= '''
SELECT tal_num FROM talonz_clin_%s WHERE talon_month=%s AND smo=%s AND talon_type > 0;
'''
GET_CODE= 'SELECT code_usl, kol_usl FROM para_clin WHERE tal_num=%s'

GET_TARIF= 'SELECT code, tarif, name FROM %s'

TEST_SELECT='''
SELECT
    tal.tal_num AS n_zap
FROM
    talonz_clin_23
WHERE
    tal.talon_type > 0 AND
    tal.talon_month=1 AND
     tal.usl_ok=3;
'''