""" module defines the class to parse BARS errors file and fill the errors table"""

import os
from datetime import datetime
#from tempfile import TemporaryFile as stmp
from tempfile import TemporaryDirectory as stmp
from flask_restful import reqparse
from flask import current_app
from werkzeug import datastructures
from werkzeug.utils import secure_filename
from poly.utils.sqlbase import SqlProvider
from poly.reestr.task import RestTask
from poly.reestr.xml.errs. sqlerrs import geterrs
from poly.utils.files import allowed_file, get_name_tail
from poly.reestr.xml.errs import config

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
        try:
            args = parser.parse_args()
        except Exception as e:
            return self.abort(400, f'Errs args parser: {e}')

        file = args['files'][0] # only first FileStorage
        filename = secure_filename(file.filename)
        if not allowed_file( filename, current_app.config ) or not filename.endswith('.xml'):
            return self.abort(400, f"Допустимое расширение имени файла .xml {filename}")

        fname = self.parse_fname(filename, 'errs')
        if isinstance(fname, str):
            return self.abort(400, fname)
        mo_code, _, _, ar, month =  fname

        sf= stmp(dir=self.cwd)
        up_file = os.path.join(sf.name, filename)
        file.save(up_file)

        try:
            rc= geterrs(
                up_file, self.sql_srv, mo_code, ar, month, ('824',), 'ignore'
            )
        except Exception as e:
            raise e
            return self.abort(500, f"Ошибка при обработке файла {filename}: {e}")
        else:
            return self.resp(filename,
                f"Файл ошибок: {filename} Записей считано {rc}", True)
        finally:
            sf.cleanup()

    def get(self):
        mo_code, year, month = ('000000', '2020', '12')
        with SqlProvider(self.sql_srv, mo_code, year, month) as _sql:
            _sql.qurs.execute(config.COUNT_ERRORS)
            rc= _sql.qurs.fetchone()

            if not bool(rc[0]):
                return self.resp('', "Нет принятых ошибок", False)

            df= str(datetime.now()).split(' ')[0]
            filename= f"ERR_{df}_{get_name_tail(5)}.csv"
            os.chdir(str(self.cwd))
            _file = os.path.join(self.cwd, filename)

            try:
                _sql.qurs.execute(config.TO_CSV % _file)
            except Exception as e:
                return self.abort(500, f"Не удалось сформировать файл ошибок: {e}")

        return self.resp(_file, "Посдение ошибки", True)
