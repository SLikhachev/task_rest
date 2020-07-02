DROP FUNCTION get_pgc( code varchar)
DROP FUNCTION get_grc( grup int )

CREATE OR REPLACE FUNCTION public.get_pgc(code_usl varchar) RETURNS 
table( 
id int, name varchar
) 
AS $$
select 
    id, name 
from 
    pmu_grup_code as pgc, 
    pmu_grup as pgr
where 
    pgc.code_usl=$1 and
    pgr.id=pgc.grup
$$ LANGUAGE SQL;      

CREATE OR REPLACE FUNCTION public.get_grc(id int) RETURNS 
table( 
id int, code_usl varchar,  name varchar, code_podr smallint, code_spec smallint,
ccode integer
) 
AS $$
select 
   pmu.id, pmu.code_usl,  pmu.name, pmu.code_podr, pmu.code_spec, pmu.ccode
from 
    pmu_grup_code as pgc, 
    pmu
where 
    pgc.grup=$1 and
    pmu.code_usl=pgc.code_usl
$$ LANGUAGE SQL;

ALTER TABLE pmu_grup_code DROP CONSTRAINT pmu_grup_code_grup_fkey;
ALTER TABLE  pmu_grup_code ADD FOREIGN KEY (grup) 
    REFERENCES pmu_grup(id) ON UPDATE  CASCADE ON DELETE CASCADE;
delete from pmu_grup_code where code_usl is null
ALTER TABLE pmu_grup_code ADD CONSTRAINT pmu_grup_code_pkey  PRIMARY KEY (grup, code_usl);
