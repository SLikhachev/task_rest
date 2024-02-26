

TRUNCATE_TARIFS='TRUNCATE TABLE tarifs_pmu_vzaimoras;'

FIELD_NAMES= ['code_usl', 'name', 'tarif']
EXTRA_DICT= {
    'code_podr': 221,
    'code_spec': 63,
    'amb': True, 'ds': False, 'stom': False,
    'date1': '2024-01-01', 'updated': '2024-01-01'
}

GET_PMU='''
SELECT id FROM pmu
WHERE code_usl='{code_usl}';
'''
INSERT_PMU='''
INSERT INTO pmu (
    code_usl, name, code_podr, code_spec,
    amb, ds, stom,
    date1)
VALUES (
    '{code_usl}', '{name}', {code_podr}, {code_spec},
    {amb}, {ds}, {stom},
    '{date1}'
);
'''
INSERT_TARIF='''
INSERT INTO tarifs_pmu_vzaimoras (
    code, tarif, name, updated)
VALUES (
    '{code}', {tarif}, '{name}', '{updated}'
);
'''

FAIL="Error import pmu"