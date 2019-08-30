TNAME = ['RR', 'RP', 'RS']

RR_INT =  [
    1, 2, 8, 9,  14, 15, 18, 19, 21, 23, 24, 25, 26, 27,
    29, 32, 34, 40, 42, 43, 44, 45, 46, 47, 48, 49,
    55, 56, 59, 61, 65, 69
]
RR_FLOAT = []

CREATE_RR = '''
CREATE TABLE IF NOT EXISTS rr%s (
    id serial PRIMARY KEY,
    nusl int,
    card int NOT NULL,
    fam varchar(32) NOT NULL,
    imya varchar(32),
    otch varchar(32),
    pol char(1) NOT NULL,
    date_birth date NOT NULL,
    kateg smallint,
    ist_fin smallint,
    c_insur char(3),
    p_ser varchar(10),
    p_num varchar(20),
    from_firm char(3),
    purp smallint NOT NULL,
    urgent smallint,
    date_in Date NOT NULL,
    date_out Date NOT NULL,
    q_u smallint,
    result_ill smallint,
    code_mes varchar(7),
    result_tre smallint,
    ds_clin varchar(15) NOT NULL,
    char_main smallint,
    visit_pol smallint DEFAULT 0,
    visit_hom smallint DEFAULT 0,
    visit_ds smallint DEFAULT 0,
    visit_hs smallint DEFAULT 0,
    nsndhosp varchar(15),
    type_hosp smallint, 
    specfic char(3) NOT NULL,
    docfic char(3) NOT NULL,
    type_pay smallint,
    d_type char(3),
    k_pr smallint, 
    visit_pr varchar(7), 
    smo varchar(8),
    npr_mo varchar(8),
    prvs varchar(8) DEFAULT 0,
    iddokt varchar(16),
    vpolis smallint,
    novor varchar(8),
    os_sluch smallint,
    profil smallint DEFAULT 0,
    det smallint,
    vidpom smallint DEFAULT 0,
    usl_ok smallint DEFAULT 0,
    ishod smallint DEFAULT 0,
    rslt smallint DEFAULT 0,
    doctype smallint,
    docser varchar(10),
    docnum varchar(20),
    snils varchar(14),
    ur_mo varchar(6),
    okato_oms varchar(5),
    vnov_d smallint,
    for_pom smallint,
    ds2 varchar(15),
    ds3 varchar(15),
    vnov_m smallint,
    code_mes2 varchar(7),
    dost smallint,
    fam_p varchar(31),
    im_p varchar(31),
    ot_p varchar(31),
    w_p smallint,
    dr_p date, 
    dost_p varchar(15),
    mr varchar(127),
    i_type smallint,
    code char(3),
    tarif numeric(10,2),
    para numeric(8,2),
    stom numeric(8,2),
    foms_price numeric(8,2)
    
)
'''
CREATE_RP = '''
CREATE TABLE IF NOT EXISTS rp%s (
    id serial PRIMARY KEY,
    nusl int NOT NULL,
    code_usl varchar(7),
    kol_usl smallint DEFAULT 1,
    uet_fakt numeric(5,2),
    executor varchar(9),
    ex_spec varchar(6),
    date_p date NOT NULL,
    date_in date NOT NULL,
    lpu	varchar(6),
    prvs varchar(9),
    iddokt varchar(17),
    profil smallint,
    code_nom	varchar(15),
    price numeric(8,2)
)
'''
CREATE_IND_RP = '''
CREATE INDEX IF NOT EXISTS rp%s_index ON rp%s (nusl)
'''
RP_INT = [ 1, 3, 12]
RP_FLOAT = [4]

CREATE_RS= '''
CREATE TABLE IF NOT EXISTS rs%s (
    id serial PRIMARY KEY,
    nusl int NOT NULL,
    code_usl varchar(8),
    zub char(3),
    kol_viz	smallint,
    uet_fakt numeric(5,2),
    date_in date NOT NULL,
    date_out date NOT NULL,
    lpu	varchar(7),
    prvs varchar(9),
    iddokt	varchar(16),
    profil smallint,
    uet numeric(5,2)
)
'''
RS_INT = [ 1, 4, 11]
RS_FLOAT = [5]

CREATE_IND_RS = '''
CREATE INDEX IF NOT EXISTS rs%s_index ON rs%s (nusl)
'''

TRUNCATE = 'TRUNCATE TABLE %s'

INSERT = 'INSERT INTO %s VALUES ('


