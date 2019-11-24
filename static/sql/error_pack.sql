CREATE TABLE IF NOT EXISTS error_pack(
  id serial primary key,
  tal_num integer,
  crd_num varchar(20),
  error varchar(511)
)
