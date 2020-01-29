SELECT 
    tal.tal_num AS idcase,
    tal.tal_num AS n_zap,
    tal.tal_num AS nhistory,
    tal.open_date as date_z_1,
    tal.close_date as date_z_2,
    tal.open_date as date_1,
    tal.close_date as date_2,
    tal.crd_num as card,
    tal.crd_num AS id_pac,
    
    tal.mek, -- as pr_nov,
    
    tal.smo as tal_smo,
    tal.polis_type,
    tal.polis_ser,
    tal.polis_num,
    tal.smo_okato,
    
    tal.doc_spec as specfic,
    
    tal.purp,
    tal.usl_ok,
    tal.for_pom as urgent,
    tal.rslt,
    tal.ishod,
    
    tal.visit_pol, 
    tal.visit_home as visit_hom,
    
    tal.npr_mo,
    tal.npr_date,
    tal.npr_mo as from_firm,
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
    crd.dul_org as docorg
        
FROM
    talonz_clin_19 as tal, 
    cardz_clin as crd, 
    spec_prvs_profil as spec,
    doctor as doc
WHERE
    tal.ist_fin=1 AND
    spec.spec=tal.doc_spec AND 
    doc.spec=tal.doc_spec AND 
    doc.code=tal.doc_code AND 
    crd.crd_num=tal.crd_num and
    crd.crd_num=tal.crd_num AND
    -- tal.talon_type > 0 AND '
    -- tal.talon_type=1 AND '
    tal.talon_month=1 order by tal.tal_num; 
    tal.talon_month=1137 order by tal.tal_num; 