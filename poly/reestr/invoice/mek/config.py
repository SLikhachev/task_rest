

COUNT_MEK= '''
    SELECT count(tal_num) from talonz_clin_%s
    WHERE talon_month=%s AND talon_type=1 AND mek=1;
'''

TO_CSV= '''COPY (
SELECT t.tal_num, t.crd_num, c.fam, t.open_date, t.close_date, t.usl_ok, t.ds1
FROM talonz_clin_%s AS t, cardz_clin AS c
WHERE t.crd_num=c.crd_num AND t.talon_month=%s AND t.mek=1
) TO'''
MEK_FILE= """ '%s' With CSV 
DELIMITER ';' HEADER QUOTE '"' FORCE QUOTE * ENCODING 'win1251'
"""

MOVE_MEK= '''
    UPDATE talonz_clin_%s
    SET talon_month=%s
    WHERE talon_month=%s AND mek=1 AND talon_type=1;
'''
