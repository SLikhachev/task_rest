BEGIN;
ALTER TABLE talonz_clin_20
DROP CONSTRAINT talonz_clin_20_crd_num_fkey,
ADD CONSTRAINT talonz_clin_20_crd_num_fkey FOREIGN KEY (crd_num)
REFERENCES public.cardz_clin (crd_num) MATCH SIMPLE
  ON UPDATE CASCADE ON DELETE NO ACTION;
 COMMIT;