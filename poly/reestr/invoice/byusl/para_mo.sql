COPY (
SELECT
    para.code_usl as code_usl, tar.name as name, tar.tarif as tarif,
    SUM(para.kol_usl) as kolvo_usl,
    SUM(para.kol_usl * tar.tarif)::numeric(12,2) as summa_usl
FROM
    talonz_clin_26 as tal,
    para_clin_26 as para
    LEFT OUTER JOIN tarifs_pmu_vzaimoras AS tar ON (tar.code = para.code_usl)
WHERE
    para.tal_num=tal.tal_num AND
    para.code_usl ILIKE 'A05%' AND
    tal.talon_type > 0 AND
    tal.npr_mo=747 AND
    tal.open_date >= '2026-04-20' AND
    tal.open_date <= '2026-05-20'
GROUP BY (para.code_usl, tar.name, tar.tarif)
ORDER BY para.code_usl
)
TO STDOUT WITH
(FORMAT  'csv', DELIMITER ';', QUOTE '"', HEADER True);
