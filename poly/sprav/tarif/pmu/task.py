""" defines a class for the some tarifs update """

import os
from datetime import date
from tempfile import TemporaryDirectory as stmp
from werkzeug.utils import secure_filename
from werkzeug import datastructures

from flask_restful import reqparse, inputs
from flask import current_app

from poly.utils.sqlbase import SqlProvider
from poly.utils.files import allowed_file
from poly.task import RestTask
#from . import config as cfg
from .import_pmu import PmuImport


parser = reqparse.RequestParser()
parser.add_argument('files', required=True, type=datastructures.FileStorage,
    location='files',  action='append', help="{Нет файла тарифов}"
)
# This param is not used yet just for future if any
parser.add_argument('table', required=True, type=str,
    choices=['tarifs_pmu_vzaimoras'],
    location=('json', 'form'), help='{Название таблицы тарифов для обоновления}'
)
# checkbox: copy table from existed one ?
parser.add_argument('copy', type=inputs.boolean, default=False, dest='copy',
    location=('json', 'form'), help='{Копировать существующую таблицу}')

class UpdateTarifs(RestTask):
    """ class def """

    def __init__(self):
        super().__init__()
        self.tmp_dir= None
        # these params we need for sql_adpater's compatabilies
        self.mo_code = current_app.config.get('ACTUAL_MO_CODE', '000000')
        self._year= date.today().year

    # upload csv file and process data
    def post(self):
        try:
            args = parser.parse_args()
        except Exception as exc:
            return self.abort(400, f'Неверные параметры запроса: {exc}')

        file = args['files'][0]  # only first FileStorage
        filename = secure_filename(file.filename)
        if not allowed_file(filename, current_app.config) or not filename.endswith('.csv'):
            return self.abort(400, f"Допустимое расширение имени файла .csv {filename}")

        #self.cwd = self.catalog('', 'reestr', 'inv')
        self.tmp_dir = stmp()
        up_file = os.path.join(self.tmp_dir.name, filename)
        file.save(up_file)

        try:
            with SqlProvider(self) as _sql: # this is sql object bot DB.connection

                # import either patients or pmus, as of the pack_type
                _import = PmuImport(_sql, up_file)
                _import.prepare_table(args.get('copy', False))
                pmus, tarifs= _import.update()
        except Exception as exc:
            raise exc
            #return self.exit(self.abort, 500, f"Ошибка сервера: {e}")

        msg = f"Файл: {filename}. Добавлено ПМУ: {pmus}, Тарифов: {tarifs}"
        return self.resp('', msg, True)

