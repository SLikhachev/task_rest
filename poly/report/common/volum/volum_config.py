BASE_DIR='volum'
TPL_DIR = 'tpl'
REPORT_DIR = 'report'
FILE_R = 'volumes'

INSURERS = {
    '016': 'ООО Страховая компания Спасские ворота-М',
    '011':  'ООО Восточно-страховой альянс',
    '012':  'СК "Милосердие"',
    '000': 'Инокраевые',
    '999': 'Итого '
}

THIS_MONTH = 'select * from p146_report where this_year=%s and this_month=%s order by insurer desc'

THIS_YEAR = '''select insurer, 
    sum(pol_ambul_visits) as pol_ambul_visits, sum(pol_stac_visits) as pol_stac_visits, 
    sum(pol_stom_uet) as pol_stom_uet, 
    sum(pol_ambul_persons) as pol_ambul_persons, sum(pol_stac_persons) as pol_stac_persons,
    sum(pol_stom_persons) as pol_stom_persons,
    sum(travma_ambul_visits) as travma_ambul_visits, sum(travma_ambul_persons) as travma_ambul_persons 
    from p146_report where this_year=%s group by insurer order by insurer DESC ;'''

_ROW = {'this_year':0, 'this_month':1, 'insurer':2,
    'pol_ambul_visits':3, 'pol_stac_visits':4, 'pol_stom_uet':5,
    'pol_ambul_persons':6,'pol_stac_persons':7,'pol_stom_persons':8,
    'travma_ambul_visits':9, 'travma_ambul_persons':10
}

TOTAL_OFFSET = 2