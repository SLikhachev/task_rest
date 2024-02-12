""" The SQL statements to move MEK tasks """


TALONZ, PMU  = 'talonz_clin', 'para_clin'


TEST_TABLE_EXISTS='''
SELECT EXISTS (
    SELECT FROM
        pg_tables
    WHERE
        schemaname = 'public' AND
        tablename  = '{}'
    );
'''

SELECT_FIELDS = '''
SELECT * FROM {} LIMIT 1;
'''

""" to prevent the second (repeated) INSERT on move between years
(the last month (12) of the previuos year and the first (1) month of the current year)
we use talon_type=1 flag, after insert we set this flag to 2 (closed talon),
so we need to update this flag to 1 manually if we need
insert ones time again (maybe some errors were there)
"""
SELECT_PREV_COND = '''
WHERE mek=1 AND talon_month=12 AND talon_type=1
ORDER BY tal_num
'''
INSERT_MEK='''
INSERT INTO {to_table} ({fields})
    SELECT {fields} FROM {from_table} %s
    RETURNING tal_num;
''' % SELECT_PREV_COND


""" The moved talons will been have talon_month = 12 (dec),
(as from table of the previuos year, 12 month),
so we need update this column an set the month to 1 (jan)
"""
UPDATE_MONTH='''
UPDATE {to_table} SET talon_month=1
WHERE talon_month=12 AND mek=1;
'''

""" We need the tal numbers for the select paraclin records
from the prev year table
"""
SELECT_TAL_NUMS = '''
SELECT tal_num FROM {table} %s;
''' % SELECT_PREV_COND

""" close the talons with MEK in the prev year 12 month
"""
UPDATE_TYPE='''
UPDATE {table} SET talon_type=2 WHERE tal_num={tal_num};
'''

""" Insert the pmus from the prev year to the current pmu table
"""
INSERT_PMU='''
INSERT INTO {to_pmu} ({pmu_fields}) VALUES (
'{tal_num}', '{date_usl}', '{code_usl}', '{kol_usl}',
'{exec_spec}', '{exec_doc}', '{exec_podr}'
);
'''

""" select pmus for tal_number
"""
SELECT_PMU = '''
SELECT * FROM {from_pmu} as t
WHERE t.tal_num={tal_num};
'''

PMU_FIELDS="tal_num, date_usl, code_usl, kol_usl, exec_spec, exec_doc, exec_podr"



COUNT_MEK= '''
    SELECT count(tal_num) from talonz_clin_%s
    WHERE talon_month=%s AND talon_type=1 AND mek=1;
'''

COPY_TO= '''COPY (
SELECT t.tal_num, t.crd_num, c.fam, t.open_date, t.close_date, t.usl_ok, t.ds1
FROM talonz_clin_%s AS t, cardz_clin AS c
WHERE t.crd_num=c.crd_num AND t.talon_month=%s AND t.mek=1 AND t.talon_type=1
) TO'''
STDOUT = """STDOUT WITH"""
MEK_FILE= """ '%s' With CSV """
CSV_OPTS = """
FORMAT 'csv', DELIMITER ';', HEADER, QUOTE '"', FORCE_QUOTE *, ENCODING 'utf-8'
"""

MOVE_MEK= '''
    UPDATE talonz_clin_%s
    SET talon_month=%s
    WHERE talon_month=%s AND mek=1 AND talon_type=1;
'''
