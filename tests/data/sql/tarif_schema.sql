BEGIN;
-- DROP TABLE IF EXISTS pmu;
DROP TABLE IF EXISTS tarifs_pmu_vzaimoras;
CREATE TABLE IF NOT EXISTS pmu (
    id serial PRIMARY KEY,
    code_usl character varying(32),
    name character varying(255),
    code_podr smallint,
    code_spec smallint,
    amb boolean,
    ds boolean,
    stom boolean,
    date1 date,
    date2 date,
    ccode integer
);
CREATE TABLE tarifs_pmu_vzaimoras (
    id serial PRIMARY KEY,
    code character varying(32) not null,
    tarif real,
    name character varying(512),
    updated date,
    cuser name
);
COMMIT;