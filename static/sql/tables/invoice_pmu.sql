CREATE TABLE IF NOT EXISTS invoice_pmu(
  code_usl character varying(20) NOT NULL primary key,
  kol_usl integer,
  tarif numeric(10,2),
  profil integer,
  prvs integer
)
