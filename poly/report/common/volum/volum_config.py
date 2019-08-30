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

THIS_MONTH = '''select
this_year, this_month, insurer,
pol_ambul_visits,
pol_prof_visits,
pol_stac_visits, 
pol_stom_uet, 
pol_ambul_persons,
pol_prof_persons,
pol_stac_persons,
pol_stom_persons,
travma_ambul_visits,
travma_ambul_persons 
from p146_report where this_year=%s and this_month=%s order by insurer desc'''

THIS_YEAR = '''select insurer, 
    sum(pol_ambul_visits) as pol_ambul_visits,
    sum(pol_prof_visits) as pol_prof_visits,
    sum(pol_stac_visits) as pol_stac_visits, 
    sum(pol_stom_uet) as pol_stom_uet, 
    sum(pol_ambul_persons) as pol_ambul_persons,
    sum(pol_prof_persons) as pol_prof_persons,
    sum(pol_stac_persons) as pol_stac_persons,
    sum(pol_stom_persons) as pol_stom_persons,
    sum(travma_ambul_visits) as travma_ambul_visits, sum(travma_ambul_persons) as travma_ambul_persons 
    from p146_report where this_year=%s and this_month < %s group by insurer order by insurer DESC ;'''

_ROW = {'this_year':0, 'this_month':1, 'insurer':2,
    'pol_ambul_visits':3, 'pol_prof_visits':4, 'pol_stac_visits':5, 'pol_stom_uet':6,
    'pol_ambul_persons':7, 'pol_prof_persons':8, 'pol_stac_persons':9, 'pol_stom_persons':10,
    'travma_ambul_visits':11, 'travma_ambul_persons':12
}

TOTAL_OFFSET = 2