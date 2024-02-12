BEGIN;
DROP TABLE IF EXISTS cardz_clin;
DROP TABLE IF EXISTS talonz_clin_22;
DROP TABLE IF EXISTS talonz_clin_23;
DROP TABLE IF EXISTS talonz_clin_24;
DROP TABLE IF EXISTS para_clin_23;
DROP TABLE IF EXISTS para_clin_24;
CREATE TABLE cardz_clin (
    id smallint PRIMARY KEY,
    crd_num varchar(20) NOT NULL,
    fam varchar(20) NOT NULL
);
CREATE TABLE talonz_clin_22 (
    tal_num smallserial PRIMARY KEY,
    crd_num varchar(20) NOT NULL,
    open_date date NOT NULL,
    close_date date NOT NULL,
    talon_month smallint NOT NULL,
    talon_type smallint NOT NULL,
    mek smallint DEFAULT 0,
    usl_ok smallint DEFAULT 0,
    ds1 varchar(8) DEFAULT 'DS23.1'
);
CREATE TABLE talonz_clin_23  (
    tal_num smallserial PRIMARY KEY,
    crd_num varchar(20) NOT NULL,
    open_date date NOT NULL,
    close_date date NOT NULL,
    talon_month smallint NOT NULL,
    talon_type smallint NOT NULL,
    mek smallint DEFAULT 0,
    usl_ok smallint DEFAULT 0,
    ds1 varchar(8) DEFAULT 'DS23.1'
);
CREATE TABLE talonz_clin_24  (
    tal_num smallserial PRIMARY KEY,
    crd_num varchar(20) NOT NULL,
    open_date date NOT NULL,
    close_date date NOT NULL,
    talon_month smallint NOT NULL,
    talon_type smallint NOT NULL,
    mek smallint DEFAULT 0,
    usl_ok smallint DEFAULT 0,
    ds1 varchar(8) DEFAULT 'DS23.1'
);
CREATE TABLE para_clin_23 (
    id smallserial PRIMARY KEY,
    tal_num smallint NOT NULL,
    date_usl date NOT NULL,
    code_usl character varying(20) NOT NULL,
    kol_usl smallint NOT NULL,
    exec_spec integer DEFAULT 0,
    exec_doc integer DEFAULT 0,
    exec_podr integer DEFAULT 0
);
CREATE TABLE para_clin_24 (
    id smallserial PRIMARY KEY,
    tal_num smallint NOT NULL,
    date_usl date NOT NULL,
    code_usl character varying(20) NOT NULL,
    kol_usl smallint NOT NULL,
    exec_spec integer DEFAULT 0,
    exec_doc integer DEFAULT 0,
    exec_podr integer DEFAULT 0
);
INSERT INTO cardz_clin (id, crd_num, fam) VALUES
    (1, '01', 'FAM-1'),
    (2, '02', 'FAM-2'),
    (3, '03', 'FAM-3'),
    (4, '04', 'FAM-4'),
    (5, '05', 'FAM-5'),
    (6, '06', 'FAM-6')
;
INSERT INTO talonz_clin_22 (tal_num, crd_num, open_date, close_date, talon_month, talon_type, mek) VALUES
    (1, '01', '2022-11-01', '2022-11-01', '11', '2', '0'),
    (2, '02', '2022-11-02', '2022-11-03', '11', '2', '0'),
    (3, '03', '2022-11-03', '2022-11-03', '11', '1', '1'),
    (4, '04', '2022-11-04', '2022-11-04', '11', '1', '1'),
    (5, '05', '2022-11-05', '2022-11-05', '11', '1', '1')
;
INSERT INTO talonz_clin_23 (tal_num, crd_num, open_date, close_date, talon_month, talon_type, mek) VALUES
    (1, '01', '2023-11-01', '2023-11-01', '11', '2', '0'),
    (2, '02', '2023-11-02', '2023-11-02', '11', '2', '0'),
    (3, '03', '2023-11-03', '2023-11-03', '11', '1', '1'),
    (4, '04', '2023-11-04', '2023-11-04', '12', '2', '1'),
    (5, '05', '2023-12-05', '2023-12-05', '12', '1', '1'),
    (6, '06', '2023-12-06', '2023-12-06', '12', '1', '1')
;
INSERT INTO para_clin_23 (tal_num, date_usl, code_usl, kol_usl)
VALUES
    (1, '2023-11-01', 'Code.1', '1'),
    (2, '2023-11-02', 'Code.2', '1'),
    (3, '2023-11-03', 'Code.3', '1'),
    (4, '2023-11-04', 'Code.4', '1'),
    (5, '2023-12-05', 'Code.5', '1'),
    (6, '2023-12-06', 'Code.6', '1')
;
COMMIT;