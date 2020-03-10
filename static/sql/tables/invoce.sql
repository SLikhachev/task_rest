CREATE TABLE invoice_bars (

n_zap int primary key,
id_pac varchar (20),
spolis varchar(10),
npolis varchar(16),
usl_ok int,
vidpom int,
for_pom int,
date_z_1 date,
date_z_2 date,
rslt int,
ishod int,
profil int,
nhistory int,
ds1 varchar(6),
prvs int,
idsp int,
sumv numeric(11, 2),
sank_it numeric(11, 2),
fam varchar(32),
im varchar(32),
ot varchar(32),
w smallint,
dr date
)

-- HM250228S25011_190722841
CREATE TABLE invoice_meta (
id serial primary key,
lpu int, 
smo int,
yar int,
mon int,
typ int
)
