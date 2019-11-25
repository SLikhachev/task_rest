CREATE TABLE IF NOT EXISTS errors_bars(
  id serial primary key,
  num varchar(15),
  name varchar(511)
)

create index errors_bars_num on errors_bars(num)

pg_dump -t errors_bars -U postgres -d hokuto > errors_bars.sql