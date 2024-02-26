""" defines a class for the pmu tarifs update """

import os
from datetime import date
from tempfile import TemporaryDirectory as stmp
from werkzeug.utils import secure_filename
from werkzeug import datastructures

from flask_restful import reqparse
from flask import current_app

from poly.utils.sqlbase import SqlProvider
from poly.utils.files import allowed_file
from poly.task import RestTask
from . import config as cfg
from .import_pmu import PmuImport


parser = reqparse.RequestParser()
parser.add_argument('files', required=True, type=datastructures.FileStorage,
    location='files',  action='append', help="{Нет файла тарифов}"
)

class UpsertTarifs(RestTask):
    """ class def """

    def __init__(self):
        super().__init__()
        self.tmp_dir= None
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
            with SqlProvider(self) as _sql:

                # import either patients or pmus, as of the pack_type
                _import = PmuImport(_sql, up_file)
                pmus, tarifs= _import.upsert()
        except Exception as exc:
            raise exc
            #return self.exit(self.abort, 500, f"Ошибка сервера: {e}")

        msg = f"Файл: {filename}. Добавлено ПМУ: {pmus}, Тарифов: {tarifs}"
        return self.resp('', msg, True)

