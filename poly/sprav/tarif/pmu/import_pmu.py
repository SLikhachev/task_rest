""" a tarifs pmu file import class definition """

from datetime import date
import re
import csv
from decimal import getcontext, Decimal, ROUND_HALF_UP
from psycopg2 import sql as psy_sql
from poly.sprav.tarif.pmu import config as cfg

code=re.compile(r'^A\d\d.\d\d.\d\d\d(.\d\d\d(.\d\d\d)?)?$')
esc=re.compile(r'[\\\"\'\&\{\}\[\]\%\(\)]')
class PmuImport:

    def __init__(self, sql: object, csvfile: str):
        """ Import a pmus and correct or insert a tarifs from csv file
            :param: sql: context manager of the DB SqlProvider
            :param: csvfile: str - abs path to the csv file
        """
        self.date1 = date.today().strftime('%Y-%m-%d')
        self.file= csvfile
        self.conn = sql._db # sql connection
        # print(self.conn)
        self.qurs = sql.qurs # sql connection cursor
        # self.trans = str.maketrans("\"\'&{}[]%()", "")


    def prepare_table(self, copy: bool):
        year = date.today().year % 100 - 1
        if copy:
            self.qurs.execute(cfg.COPY_TARIF_TABLE, (year, year))

        # truncate table anyway
        self.qurs.execute(cfg.TRUNCATE_TARIF_TABLE)
        self.conn.commit()

    def cleanup_csv_line(self, line: int, rec: dict):
        #getcontext().prec = 2
        rec['code_usl'] = rec['code_usl'].strip().upper()
        assert code.match(rec['code_usl']), f"Некорректный код услуги {rec['code_usl']}, строка {line}"
        # re.sub(r'[\"\'\&\{\}\[\]\%\(\)]', '', r'"\'&{}[]%(){}()**+_+')
        rec['name'] = re.sub(esc, '', rec['name'].strip())
        try:
            pass
            #rec['tarif'] = Decimal(rec['tarif'])
            #print (tarif)
            #rec['tarif'] = Decimal(tarif)
        except Exception as exc:
            raise exc #Exception(f"Некорректный тариф {rec['tarif']}, строка {line}") from exc

    def update(self) -> tuple:
        """ returns tuple of 1 if any errors occured
            else records count and meta info
        """
        with open(self.file, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile,
                fieldnames=cfg.FIELD_NAMES,
                delimiter=';'
            )
            pmu = tarif = 0
            for row in reader:
                self.cleanup_csv_line(reader.line_num, row)
                row.update(cfg.EXTRA_DICT)
                row['code'] = row['code_usl']
                row['updated'] = self.date1
                stmt = cfg.GET_PMU.format(**row)
                self.qurs.execute(stmt)
                res = self.qurs.fetchone()
                #res, pp = False, False
                try:
                    if not res:
                        self.insert_pmu(row)
                        pmu +=1
                    stmt = cfg.INSERT_TARIF.format(**row)
                    self.qurs.execute(stmt)
                except Exception as exc:
                    raise exc
                    raise f"Ошибка {exc}  строка \
                        {reader.line_num}: {row['code_usl']}, {row['name']}, {row['tarif']}"
                    #print(stmt)
                self.conn.commit()
                tarif +=1

        return self.close(pmu, tarif)

    def insert_pmu(self, row):
        stmt= cfg.INSERT_PMU.format(**row)
        self.qurs.execute(stmt)

    def close(self, pmu, tarif) -> tuple:
        self.conn.commit()
        return pmu, tarif
