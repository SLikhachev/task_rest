

GET_TARIF_TABLES='''
SELECT tablename AS table FROM pg_tables
  WHERE tablename ilike 'tarifs_pmu_vzaimoras%';
'''

RENAME_TARIF_TABLE='''
DO $$
BEGIN
IF NOT EXISTS (
  SELECT 1 FROM pg_tables WHERE tablename = 'tarifs_pmu_vzaimoras_%s'
) THEN EXECUTE
  'ALTER TABLE tarifs_pmu_vzaimoras RENAME TO tarifs_pmu_vzaimoras_%s';
END IF;
END$$;
'''

COPY_TARIF_TABLE='''
BEGIN;
CREATE TABLE IF NOT EXISTS tarifs_pmu_vzaimoras
  (LIKE tarifs_pmu_vzaimoras_%s INCLUDING ALL);
-- ALTER TABLE tarifs_pmu_vzaimoras ALTER COLUMN id DROP DEFAULT;
-- CREATE SEQUENCE IF NOT EXISTS tarifs_pmu_vzaimoras_id_seq AS integer;
-- ALTER TABLE tarifs_pmu_vzaimoras ALTER COLUMN id SET DEFAULT nextval('tarifs_pmu_vzaimoras_id_seq'::regclass);
-- ALTER TABLE tarifs_pmu_vzaimoras ADD CONSTRAINT tarifs_pmu_vzaimoras_code UNIQUE (code);
COMMIT;
'''

TRUNCATE_TARIF_TABLE='TRUNCATE TABLE tarifs_pmu_vzaimoras;'

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