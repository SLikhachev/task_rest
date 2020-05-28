ALTER TABLE doctor DROP CONSTRAINT doctor_spec_fkey

ALTER TABLE  doctor ADD FOREIGN KEY (spec) 
    REFERENCES spec_prvs_profil(spec) ON UPDATE  CASCADE;
