
GET_XML_TASK='''SELECT yar FROM invoice_meta WHERE lpu= %s;
'''
# set typ to running task
SET_XML_TASK='''UPDATE invoice_meta SET yar=%s WHERE  lpu =%s;
'''

select_count ='SELECT COUNT(*) FROM %s WHERE ist_fin=1'
"""
tal_num, crd_num, open_date, close_date, smo, talon_type, talon_month, 

ist_fin, first_vflag, finality, 

doc_spec, doc_code, purp, usl_ok, for_pom, rslt, ishod, 

visit_pol, pol_days, visit_home, home_days, 
visit_homstac, visit_daystac, days_at_homstac, days_at_daystac

npr_mo,  npr_spec, naprlech, 
hosp_mo, nsndhosp,extr, 

prof_k, ksk float, ksg, sh, 

ds0, ds1, ds2, ds3, char1, char2,

code_mes1, code_mes2, 

travma_type, patient_age, 

d_type, 
"""

get_hpm_data="""
SELECT 
    tal.tal_num AS idcase,
    tal.tal_num AS n_zap,
    tal.tal_num AS nhistory,
    tal.open_date as date_z_1,
    tal.close_date as date_z_2,
    tal.open_date as date_1,
    tal.close_date as date_2,
    tal.crd_num as card,
    -- tal.crd_num AS id_pac,
    
    tal.mek, -- as pr_nov,
    
    tal.smo as tal_smo,
    tal.polis_type,
    tal.polis_ser,
    tal.polis_num,
    tal.smo_okato,
    
    tal.doc_spec as specfic,
    
    tal.purp,
    tal.usl_ok,
    tal.for_pom,
    tal.rslt,
    tal.ishod,
    
    tal.visit_pol, 
    tal.visit_home as visit_hom,
    
    tal.npr_date,
    tal.npr_mo as cons_mo,
    tal.hosp_mo,
    tal.naprlech,
    tal.nsndhosp,
    tal.d_type,
    tal.ds1,
    tal.ds2,
    tal.char1 as c_zab,
    
    spec.prvs,
    spec.profil,
    doc.snils as iddokt,
    
-- PACIENT
    crd.smo as smo,
    crd.polis_type as vpolis,
    crd.polis_num as npolis,
    crd.polis_num as id_pac,
    crd.polis_ser as spolis,
    crd.st_okato,
    crd.smo_ogrn,
    crd.smo_okato as smo_ok, 
    crd.smo_name as smo_nam,
    crd.fam, 
    crd.im,
    crd.ot,
    crd.gender as pol,
    crd.birth_date as dr,
    crd.dost as dost,
    crd.dul_type as doctype,
    crd.dul_serial as docser,
    crd.dul_number as docnum,
    crd.dul_date as docdate,
    crd.dul_org as docorg,
    crd.mo_att
        
FROM
    talonz_clin_%s as tal, 
    cardz_clin as crd, 
    spec_prvs_profil as spec,
    doctor as doc
WHERE
    tal.ist_fin=1 AND
    spec.spec=tal.doc_spec AND 
    doc.spec=tal.doc_spec AND 
    doc.code=tal.doc_code AND 
    crd.crd_num=tal.crd_num AND
"""
all_tal= ' tal.talon_type > 0 AND '
fresh= ' tal.talon_type=1 AND '
month= ' tal.talon_month=%s order by tal.tal_num; --limit 1;'

get_npr_mo= 'SELECT code FROM mo_local WHERE scode=%s;'

"""
select
vpom.vidpom, 
from
vpom_profil as vpom,
where
vpom.usl_ok=tal.usl_ok AND 
vpom.profil=spec.profil AND
vpom.mo_scode = % s and
"""
#tal_num, date_usl, code_usl, kol_usl, exec_spec, exec_doc, exec_podr#
# PM USL idserv, executor, ex_spec (from talon), rl
get_usl = """
SELECT
    usl.date_usl,
    usl.code_usl, 
    usl.kol_usl, 
    usl.exec_spec as spec, 
    usl.exec_doc as doc,
    usl.exec_podr as podr,
    tal.npr_mo,
    tal.npr_spec,
    tar.tarif as sumv_usl
FROM
    para_clin_%s as usl, 
    talonz_clin_%s as tal,
    tarifs_pmu_vzaimoras as tar
WHERE
    tal.tal_num = usl.tal_num AND
    tar.code = usl.code_usl AND
    tal.tal_num=%s
"""

get_spec_usl = """
SELECT
    tal.open_date as date_usl,
    prof.one_visit as code_usl1,
    prof.two_visit as code_usl2,
    1 as kol_usl, 
    prof.podr as podr, 
    tal.doc_spec as spec,
    tal.doc_code as doc
FROM
    talonz_clin_%s as tal, profil as prof, spec_prvs_profil as spp
WHERE 
    tal.doc_spec = spp.spec AND
    prof.id = spp.profil AND 
    tal.tal_num=%s
"""

get_stom = ''

mark_as_sent="UPDATE talonz_clin_%s SET talon_type=2 WHERE tal_num=%s"

set_error="INSERT INTO error_pack(tal_num, crd_num, error) VALUES ( %s, %s, %s );"

truncate_errors="TRUNCATE TABLE error_pack;"