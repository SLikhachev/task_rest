""" defines import export invoice's files class """

import os
from tempfile import TemporaryDirectory as stmp
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug import datastructures
from flask_restful import reqparse
from poly.utils.sqlbase import SqlProvider
from poly.utils.files import allowed_file
from poly.task import RestTask
from poly.reestr.invoice.impex import config

from poly.reestr.invoice.impex.import_invoice import XmlImport
from poly.reestr.invoice.impex.export_invoice import SqlExportInvoice
from poly.reestr.invoice.impex.export_pmus import SqlExportPmus


parser = reqparse.RequestParser()
parser.add_argument('pack', type=int,
    default=1, location='form',
    help="{Тип фала счета: 1-АПП 2-Онкология ...}")
parser.add_argument('files', required=True, type=datastructures.FileStorage,
    location='files',  action='append',  help="{Нет файла счета}"
)
#correct SMO flag not used
#csmo = bool(request.form.get('csmo', 0))

class InvImpex(RestTask):
    """ class def """

    def __init__(self):
        super().__init__()

    # upload file
    def post(self):
        try:
            args = parser.parse_args()
            #correct SMO flag not used here
            csmo = False
            pack_type = args['pack']
        except Exception as exc:
            return self.abort(400, f'Неверные параметры запроса: {exc}')

        file = args['files'][0]  # only first FileStorage
        filename = secure_filename(file.filename)
        if not allowed_file(filename, current_app.config) or not filename.endswith('.zip'):
            return self.abort(400, f"Допустимое расширение имени файла .zip {filename}")

        fname= self.parse_fname(filename, 'invs')
        if len(fname) == 0:
            return self.abort(400, f"Имя файла не соответствует шаблону: {filename}")

        mo_code, _, self.smo, _ar, self.month = fname
        if mo_code not in current_app.config['MOS'].keys():
            """ in the moment the 'mo_code' must be key in config dict kind of
                MOS: {'250999': ('3334445556667',)}
                where keys: mo_code, values: tuple('MO OGRN',)
            """
            return self.abort(400, f"Код МО: {mo_code}, не зарегистрирован")

        self.year= f'20{_ar}'

        # save file to disk
        self.cwd = self.catalog('', 'reestr', 'inv')
        self._tmp_dir = stmp(dir=self.cwd)
        up_file = os.path.join(self._tmp_dir.name, filename)
        file.save(up_file)

        self._year = _ar
        self.mo_code= mo_code

        try:
            with SqlProvider(self) as _sql:

                # import either patients or pmus, as of the pack_type
                _import = XmlImport(_sql, up_file, pack_type, _ar)
                imp_recs, done= _import.invoice()
                if not done:
                    return self.exit(self.abort, 400 , config.FAIL[ imp_recs[0]])

                # export DB table to xlsx
                exp_recs, _reestr= self.export(_sql, pack_type, mo_code)
                if exp_recs < 0:
                    # error of
                    return self.exit(self.resp, '', _reestr, False)
        except Exception as exc:
            raise exc
            #return self.exit(self.abort, 500, f"Ошибка сервера: {e}")

        return self.exit(self.resp, _reestr,
            f"Счет {filename}. Записей в счете {imp_recs[0]}, (МЭК {imp_recs[1]}),\
            записей в реестре {exp_recs}.", True)


    def export(self, sql, pack_type, mo_code):
        if pack_type == 6:
            return SqlExportPmus(
                current_app, sql, mo_code, self.smo,
                self.month, self.year, 6, self.cwd
            ).export()

        return SqlExportInvoice(
            current_app, sql, mo_code, self.smo,
            self.month, self.year, pack_type, self.cwd
        ).export()


    def exit(self, fn, *args):
        os.chdir(self.cwd)
        self._tmp_dir.cleanup()
        return fn(*args)

    def get(self):
        raise NotImplemented("Метод не реализован")
