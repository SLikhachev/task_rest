

alter table cardz_clin drop constraint cardz_clin_smo_fkey;

update cardz_clin set smo=25011 where smo=25016;

alter table cardz_clin add constraint cardz_clin_smo_fkey
FOREIGN KEY ( smo ) REFERENCES smo_rf(smocod);

INSERT INTO smo_rf (tf_okato, smocod, name_smok)
VALUES (0,0,'SMO UNDEFINED');
