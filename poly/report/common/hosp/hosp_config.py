SMO = {
'ООО Страховая компания Спасские ворота-М': 16,
'ООО Восточно-страховой альянс': 11
}
BASE_DIR='hosp'
TPL_DIR = 'tpl'
REPORT_DIR = 'report'
FILE_R = 'hosp'

MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

INSUR = {
    'ООО Страховая компания Спасские ворота-М': '016',
    'ООО Восточно-страховой альянс': '011',
    'СК "Милосердие"': '012'
}
GET_MO = '''
SELECT DISTINCT hsp.to_mo, mol.name
    FROM hospital AS hsp, mo_local AS mol
    WHERE hsp.to_mo = mol.scode
    ORDER BY hsp.to_mo
'''
GET_HOSP = '''
SELECT
    hsp.fam, hsp.im, hsp.ot, hsp.date_birth,
    hsp.ds, hsp.usl_ok,
    hsp.nap_num, hsp.nap_date, hsp.for_pom_hospl,
    doc.family as doc_fam
FROM
    hospital AS hsp, doctor AS doc
WHERE
    doc.spec=cast (split_part(hsp.specfic, '.', 1) as integer) AND
    doc.code=cast (split_part(hsp.specfic, '.', 2) as integer) AND
    hsp.to_mo = %s ORDER BY hsp.nap_date
'''