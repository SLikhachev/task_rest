""" module defines the class to parse BARS errors file and fill the errors table"""

import os
from types import SimpleNamespace as NS
from datetime import datetime
from tempfile import gettempdir
from tempfile import TemporaryDirectory as stmp
from pathlib import Path
from shutil import copyfile
from flask_restful import reqparse
from flask import current_app
from werkzeug import datastructures
from werkzeug.utils import secure_filename
from poly.utils.sqlbase import SqlProvider
from poly.task import RestTask
from poly.reestr.xml.errs. sqlerrs import XmlErrors
from poly.utils.files import allowed_file, get_name_tail
from poly.reestr.xml.errs import config

# req args
parser = reqparse.RequestParser()
parser.add_argument('ptype', type=int,
    choices=(1, 2), default=1, location='form',
    help="{Тип фала с ошибками: 1-АПП 2-Онкология}")
parser.add_argument('files', required=True, type=datastructures.FileStorage,
    location='files',  action='append',  help="{Нет файла ошибок}"
)

class ErrsXml(RestTask):
    """ class definition """

    def __init__(self):
        super().__init__()
        self.cwd = self.catalog('', 'reestr', 'vmx')
        self.sql_srv['errors_table'] = config.ERRORS_TABLE_NAME

    def post(self):
         # POST to upload error file and fill the DB error_table
        try:
            args = parser.parse_args()
        except Exception as exc:
            return self.abort(400, f'Неверный запрос: {exc}')

        file = args['files'][0] # only first FileStorage
        filename = secure_filename(file.filename)
        if not allowed_file( filename, current_app.config ) or not filename.endswith('.xml'):
            return self.abort(400, f"Допустимое расширение имени файла .xml {filename}")

        fname = self.parse_fname(filename, 'errs') # tuple or str
        if isinstance(fname, str):
            return self.abort(400, fname)
        # destruct tuple
        mo_code, _, _, _ar, month =  fname

        # make tmp dir and save file to there
        _tmp_dir= stmp(dir=self.cwd)
        up_file = os.path.join(_tmp_dir.name, filename)
        file.save(up_file)
        print(f'\n -- ERR_FILE: {up_file}\n')
        try:
            xml_errors = XmlErrors(self,
                up_file, mo_code, _ar, month, ('824',), 'ignore'
            )
            errors_cnt= xml_errors.process_errors_file()
        except Exception as exc:
            raise exc
            #return self.abort(500, f"Ошибка при обработке файла {filename}: {e}")
        else:
            return self.resp(filename,
                f"Файл ошибок: {filename} Записей считано {errors_cnt}", True)
        finally:
            _tmp_dir.cleanup()


    def get(self):
        # GET to return content of the DB error_table in csv format
        # def values
        self.sql = self
        self.mo_code = '000000',
        self._year = '2020',
        self.month = '12'

        with SqlProvider(self) as _sql:

            _sql.qurs.execute(config.COUNT_ERRORS)
            errors_cnt= _sql.qurs.fetchone()
            print(errors_cnt)
            if not errors_cnt[0]:
                return self.resp('', "Нет принятых ошибок", False)

            _date = str(datetime.now()).split(' ')[0]
            filename= f"ERR_{_date}_{get_name_tail(5)}.csv"
            #_file = os.path.join(self.cwd, filename)
            # _sql.execute has not rights to write to cwd (as postgres user i believe)
            # so write to /tmp
            _src = os.path.join(gettempdir(), filename)

            try:
                _sql.qurs.execute(config.TO_CSV % _src)
                _sql._db.commit()
                assert Path(_src).exists(), 'Ошибка экспотра в CSV не сформирован файл ошибок'
                os.chdir(str(self.cwd))
                _dst = os.path.join(self.cwd, filename)
                copyfile(_src, _dst)
            except Exception as exc:
                return self.abort(500, f"Не удалось сформировать файл ошибок: {exc}")

        return self.resp(_dst, "Посдение ошибки", True)
