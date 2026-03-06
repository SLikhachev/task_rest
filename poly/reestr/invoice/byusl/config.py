
PACK_TYPE=5

GET_YEAR_USL= '''
SELECT
    para.code_usl as code_usl, tar.name as name, tar.tarif as tarif,
    SUM(para.kol_usl) as kolvo_usl,
    SUM(para.kol_usl * tar.tarif)::numeric(12,2) as summa_usl
FROM
    {talons_table} as tal,
    {para_table} as para
    LEFT OUTER JOIN {tarifs_table} AS tar ON (tar.code = para.code_usl)
WHERE
    para.tal_num=tal.tal_num AND
--  tar.code = para.code_usl AND
    para.code_usl ILIKE '{icode}' AND
    tal.talon_type {talon_type}
    {by_month}
GROUP BY (para.code_usl, tar.name, tar.tarif)
ORDER BY para.code_usl;
'''

ICODES={
    'A05%': ("Магнитно-резонансеая томография","МРТ"),
    'A06%': ("Компьютерная томография","КТ")
}

YEAR_TABLES ={
    'talons_table': 'talonz_clin_{year}',
    'para_table': 'para_clin_{year}',
    'tarifs_table': 'tarifs_pmu_vzaimoras{tarifs}'
}

TEST_TABLE_EXISTS='''
SELECT EXISTS (
    SELECT FROM
        pg_tables
    WHERE
        schemaname = 'public' AND
        tablename  = '{}'
    );
'''

BY_MONTH='''
AND tal.talon_month={month}
'''