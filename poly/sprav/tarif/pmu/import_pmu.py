""" a tarifs pmu file import class definition """

import os
import csv
from psycopg2 import sql as psy_sql
from poly.sprav.tarif.pmu import config as cfg


class PmuImport:

    def __init__(self, sql: object, csvfile: str):
        """ Import a pmus and correct or insert a tarifs from csv file
            :param: sql: context manager of the DB SqlProvider
            :param: csvfile: str - abs path to the csv file
        """
        self.file= csvfile
        self.sql = sql
        self.qurs = sql.qurs

    def upsert(self) -> tuple:
        """ returns tuple of 1 if any errors occured
            else records count and meta info
        """
        with open(self.file, encoding='utf-8') as csvfile:
            self.qurs.execute(cfg.TRUNCATE_TARIFS)
            self.sql._db.commit()
            reader = csv.DictReader(csvfile,
                fieldnames=cfg.FIELD_NAMES,
                delimiter=';'
            )
            pmu = tarif = 0
            for row in reader:
                row.update(cfg.EXTRA_DICT)
                row['code'] = row['code_usl']
                stmt = cfg.GET_PMU.format(**row)
                self.qurs.execute(stmt)
                res = self.qurs.fetchone()
                #res, pp = False, False
                if not res:
                    self.insert_pmu(row)
                    pmu +=1
                stmt = cfg.INSERT_TARIF.format(**row)
                try:
                    self.qurs.execute(stmt)
                except:
                    print(stmt)
                    raise
                self.sql._db.commit()
                tarif +=1

        return self.close(pmu, tarif)

    def insert_pmu(self, row):
        stmt= cfg.INSERT_PMU.format(**row)
        self.qurs.execute(stmt)

    def close(self, pmu, tarif) -> tuple:
        self.sql._db.commit()
        return pmu, tarif
