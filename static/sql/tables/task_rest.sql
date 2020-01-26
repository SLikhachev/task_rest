CREATE tABLE IF NOT EXISTS pack_type (
id serial PRIMARY KEY,
name varchar(15) NOT NULL,
descr varchar( 127 )
)

INSERT INTO pack_type (name, descr) VALUES
('ambul', 'Амбулаторный'),
('onko', 'Онкология'),
('day_stac', 'Дневной стационар'),
('prof', 'Профосмотр'),
('foms', 'Инокраевые'),
('pmu_vzaimo', 'ПМУ Взаиморасчеты');


CREATE TABLE IF NOT EXISTS task_rest (
id serial PRIMARY KEY,
task varchar(15) NOT NULL UNIQUE,
name varchar(127),
running int NOT NULL default 0,
last_run date default current_date,
task_year int,
task_month int,
smo int,
pack_num int,
pack_type int REFERENCES pack_type(id),
file_name varchar(127)
)
 insert into task_rest (task, name) VALUES 
 ('make_xml', 'Формируем/проверяем пакет XML.ZIP для ФОМС' ),
 ('import_errors', 'Импортитуем файл ошибок БАРС VMX.XML'),
 ('import_invoice', 'Импортируем файл счета БАРС HHM.ZIP'),
 ('self_calc', 'Собственный расчет реестра ');
 
 