
ERRORS_TABLE_NAME= 'vmx_errors'

GET_TALON= '''
SELECT
tal.tal_num, tal.crd_num, tal.open_date, tal.close_date, crd.fam
FROM %s AS tal, %s AS crd
'''
TAL= ' WHERE tal.tal_num=%s AND tal.crd_num=crd.crd_num;'

WRITE_ERROR= '''
INSERT INTO vmx_errors
(tal_num, open_date, close_date, crd_num, fam, error, cmt, cuser) VALUES
(%s, %s, %s, %s, %s, %s, %s, %s);
'''

GET_ERROR_NAME='''
SELECT name FROM errors_bars WHERE num=%s;
'''

COUNT_ERRORS= 'SELECT count(id) FROM vmx_errors'

VMX_TBL = 'vmx_errors'
VMX_COLS = ('tal_num', 'crd_num', 'fam', 'open_date', 'close_date', 'error', 'cmt')
VMX_SEP=';'
VMX_NULL=''

TO_CSV= '''COPY (
select tal_num, crd_num, fam, open_date, close_date, error, cmt from vmx_errors ) to
'%s' With CSV
DELIMITER ';' HEADER QUOTE '"' FORCE QUOTE * ENCODING 'win1251'
'''

TO_PRG_CSV= '''COPY (
select tal_num, crd_num, fam, open_date, close_date, error, cmt from vmx_errors ) to
PROGRAM 'gzip > %s' With CSV
DELIMITER ';' HEADER QUOTE '"' FORCE QUOTE * ENCODING 'win1251'
'''
#&& chmod 755 %s

MARK_TALON= "UPDATE %s SET talon_type=1 WHERE tal_num="