CREATE TABLE IF NOT EXISTS public.para_clin_21
(
  id serial PRIMARY KEY, 
  tal_num integer NOT NULL,
  date_usl date NOT NULL,
  code_usl character varying(20) NOT NULL,
  kol_usl smallint NOT NULL DEFAULT 1,
  exec_spec integer,
  exec_doc integer,
  exec_podr integer
)
