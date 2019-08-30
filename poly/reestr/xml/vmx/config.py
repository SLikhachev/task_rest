TRUNCATE_ERROR= 'TRUNCATE TABLE vmx_errors;'

GET_TALON= '''
SELECT
tal.tal_num, tal.crd_num, tal.open_date, tal.close_date, crd.fam
FROM %s AS tal, %s AS crd
'''
TAL= ' WHERE tal.tal_num=%s AND tal.crd_num=crd.crd_num;'

WRITE_ERROR= '''
INSERT INTO vmx_errors
(tal_num, open_date, close_date, crd_num, fam, error, cmt) VALUES
(%s, %s, %s, %s, %s, %s, %s);
'''

TO_CSV= '''COPY (
select tal_num, crd_num, fam, open_date, close_date, error, cmt from vmx_errors ) to 
'%s' With CSV 
DELIMITER ';' HEADER QUOTE '"' FORCE QUOTE * ENCODING 'win1251'
'''
