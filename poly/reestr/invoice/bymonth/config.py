
PACK_TYPE=4

GET_MONTH_USL= '''
SELECT
    count(tal.tal_num) AS ntal,
    mo_local.code as mo_code,
    mo_local.sname as mo_name,
    sum(tarp.tarif) as sum_usl
FROM {talons_table} as tal,
    {para_table} as para,
    tarifs_pmu_vzaimoras as tarp,
    mo_local
WHERE
    tal.talon_month={month} AND --int
    tal.tal_num=para.tal_num AND
    tal.talon_type>0 AND
    mo_local.scode=tal.npr_mo AND
    para.code_usl=tarp.code AND
    para.code_usl ilike '{icode}'
    GROUP BY mo_local.scode;
'''

# code usls
ICODES={
    'A05%': ("Магнитно-резонансная томография","МРТ"),
    'A06%': ("Компьютерная томография","КТ")
}