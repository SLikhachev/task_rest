""" The aux task's funcs to move mek """

import os
from datetime import datetime
from pathlib import Path
from flask import current_app

from poly.reestr.invoice.mek import config
from poly.utils.sqlbase import SqlProvider
from poly.utils.files import get_name_tail


class CarryMek:
    """ The class for MEKs processing """

    def __init__(self, data: object):
        """ @params:
            :data: object - MoveMek(RestTask) instance
        """
        self.data = data
        self.from_month = data.from_month
        self.to_month = data.to_month
        self.from_year = data.from_year - 2000
        self.to_year = data.to_year - 2000
        self.this_year = data.this_year - 2000
        self.from_last= self.this_year - self.from_year

        self.from_table = f'{config.TALONZ}_{self.from_year}'
        self.to_table = f'{config.TALONZ}_{self.to_year}'
        self.from_pmu = f'{config.PMU}_{self.from_year}'
        self.to_pmu = f'{config.PMU}_{self.to_year}'
        self.mek_cnt = 0

        self.sql = SqlProvider(self.data.sql).connect()
        self.qurs = self.sql.qurs
        self.db = self.sql._db

    def month_to_str(self, month: int=0) -> str:
        """ int (1-12) to month's name string
        """
        m = month if bool(month) else self.from_month
        return  f'{current_app.config["MONTH"][m-1]} {self.data.from_year}'


    def check_meks(self) -> str:
        """ check the target tables exists
        """
        for table in (self.from_table, self.to_table):
            self.qurs.execute(config.TEST_TABLE_EXISTS.format(table))
            res=self.qurs.fetchone()
            if not res.exists:
                return f'Нет целевой таблицы {table}'

        # check the records present
        self.qurs.execute(config.COUNT_MEK, (self.from_year, self.from_month))
        mc= self.qurs.fetchone()
        if (mc is None) or mc[0] == 0:
            return f'Нет записей с МЭК за месяц {self.month_to_str()}'
        self.mek_cnt=mc[0]
        return ''


    def meks_to_csv(self) -> tuple:
        """ export the meks records to CSV file,
        """
        cwd = self.data.catalog('', 'reestr', 'mek')
        df= str(datetime.now()).split(' ', maxsplit=1)[0]
        copy_to = config.COPY_TO % (self.from_year, self.from_month)
        copy_to = f'{copy_to} {config.STDOUT} ({config.CSV_OPTS});'
        #print(f'\n{copy_to}\n')
        filename= f"MEK_{df}_{get_name_tail(4)}.csv"
        file = os.path.join(cwd, filename)
        try:
            with open(file, 'w', encoding='UTF8') as _file:
                self.qurs.copy_expert(copy_to, _file)
            assert Path(file).exists(), 'Ошибка экспотра в CSV файл не сформирован'
        except Exception as exc:
            raise exc
            #return self.abort(500, f'Ошибка формирования файла МЭК')
        else:
            return file,  f"МЭК за месяц {self.month_to_str()}, записей в файле {self.mek_cnt}"
        finally:
            self.db_close()


    def check_dates(self) -> str:
        """ validate dates for the mek moving
        """
        if self.this_year != self.to_year:
            return "Переносить МЭК можно только на текущий год"
        print(f'from_last: {self.from_last}')
        print(f'from: {self.from_month} to: {self.to_month}')

        if self.from_last > 1:
            return "Переносить МЭК можно только на один год вперед"

        if self.from_last == 1:
            if self.from_month != 12 or self.to_month !=1:
                return "Переносить МЭК на год вперед можно только с декабря на январь"
            return ''

        if self.from_last == 0:
            if self.to_month <= self.from_month:
                return "Переносить МЭК можно только вперед по месяцам"
            if self.to_month > 12:
                return "Попытка перенести МЭК после декабря текущего года"
        else: # may be negative
            return "Переносить МЭК можно только вперед по годам"

        return ''


    def move_mek(self) -> str:
        """ the common transfer function
        """
        try:
            if bool(self.from_last):
                rc = self.move_mek_from_prev_year()
            else:
                rc = self.move_mek_in_current_year()
            return f'Пернесли МЭКи на {self.month_to_str(self.to_month)} {self.data.to_year}: записей {rc}.'
        except Exception as exc:
            raise exc
        finally:
            self.db_close()


    def move_mek_in_current_year(self) -> int:
        """ simply set the month field to the required from data.from_moth to data.to_month
        """
        q = config.MOVE_MEK % (self.from_year, self.to_month, self.from_month)
        self.qurs.execute(q)
        self.db.commit()
        return self.qurs.rowcount


    def insert_talonz(self) -> list:
        """ insert talons to the current year table
        """
        # select keys from table
        self.qurs.execute(config.SELECT_FIELDS.format(self.from_table))
        res=self.qurs.fetchone()

        # construct query
        fields = ",".join(list(res._fields)[1:])
        q = config.INSERT_MEK.format(from_table=self.from_table, to_table=self.to_table, fields=fields)

        # execute insert talonz
        self.qurs.execute(q)
        self.db.commit()
        return self.qurs.fetchall()
        # should retun iserted tal_nums


    def move_mek_from_prev_year(self) -> int:
        """ transefr mek records from prev to current year
        """
        inserted_this_year = self.insert_talonz()
        assert inserted_this_year, "Неудалось внести талоны в текущий год"

        # insert pmu from old to new table
        # select tal_nums from old talonz table
        self.qurs.execute(config.SELECT_TAL_NUMS.format(table=self.from_table))
        fetched_prev_year = self.qurs.fetchall()
        assert len(inserted_this_year) == len(fetched_prev_year), "Разное количество талонов в годах"

        for idx, tal_from in enumerate(fetched_prev_year):
            tal_num_from = tal_from.tal_num
            # should be same records with differnt tal_nums from old and new tables
            tal_num_to = inserted_this_year[idx].tal_num

            # then fetch all pmu with that tal_num (from old table)
            self.qurs.execute(config.SELECT_PMU.format(
                from_pmu=self.from_pmu, tal_num=tal_num_from))
            pmus = self.qurs.fetchall()
            assert len(pmus) > 0, \
                f"Ошибка: для старого талона {tal_num_from} нет записей в таблице ПМУ {self.from_pmu}"

            # then insert all fetched to the new table with new tal_num ref
            for pmu in pmus:
                q = config.INSERT_PMU.format(
                    to_pmu=self.to_pmu, pmu_fields=config.PMU_FIELDS,
                    tal_num=tal_num_to, date_usl=pmu.date_usl, code_usl=pmu.code_usl,
                    kol_usl=pmu.kol_usl, exec_spec=pmu.exec_spec,
                    exec_doc=pmu.exec_doc, exec_podr=pmu.exec_podr
                )
                self.qurs.execute(q)

            # update type in old table to prevent maybe second tarnsfer
            self.qurs.execute(config.UPDATE_TYPE.format(table=self.from_table, tal_num=tal_num_from))

            # commit trans and increase index
            self.db.commit()

    # and finally update month in target table
        self.qurs.execute(config.UPDATE_MONTH.format(to_table=self.to_table))
        self.db.commit()

        return len(fetched_prev_year)


    def db_close(self):
        """ close sql provider """
        self.qurs.close()
        self.db.close()
