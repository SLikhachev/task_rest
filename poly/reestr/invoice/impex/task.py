
import os
from tempfile import TemporaryDirectory as stmp
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug import datastructures
from flask_restful import reqparse
from poly.utils.sqlbase import SqlProvider
from poly.reestr.task import RestTask
from poly.reestr.invoice.impex.imp_inv import imp_inv
from poly.reestr.invoice.impex.exp_usl import exp_usl
from poly.reestr.invoice.impex.exp_inv import exp_inv
#from poly.reestr.invoice.impex.correct_ins import correct_ins
from poly.reestr.invoice.impex import config
from poly.utils.files import allowed_file


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

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
            csmo = False
            pack_type = args['pack']
        except Exception as e:
            return self.abort(400, f'Impex args parser: {e}')

        file = args['files'][0]  # only first FileStorage
        filename = secure_filename(file.filename)
        if not allowed_file(filename, current_app.config) or not filename.endswith('.zip'):
            return self.abort(400, f"Допустимое расширение имени файла .zip {filename}")

        fname= self.parse_fname(filename, 'invs')
        if len(fname) == 0:
            return self.abort(400, f"Имя файла не соответствует шаблону: {filename}")

        mo_code, lpu, self.smo, ar, self.month = fname
        if mo_code not in current_app.config['MOS'].keys():
            return self.abort(400, f"Код МО: {mo_code}, не зарегистрирован")

        self.year= f'20{ar}'

        # save file to disk
        self.cwd = self.catalog('', 'reestr', 'inv')
        self.sf = stmp(dir=self.cwd)
        up_file = os.path.join(self.sf.name, filename)
        file.save(up_file)

        wc = 0
        dc = rc = (0, 0)
        try:
            with SqlProvider(self.sql_srv, mo_code, self.year, self.month ) as _sql:
                # returns either invoice or usl data
                rc, res= imp_inv(up_file, _sql, pack_type, ar)
                if not res:
                    return self.exit(self.abort, 400 , config.FAIL[ rc[0]])

                if pack_type == 6:
                    wc, xreestr = exp_usl(
                        current_app, _sql, mo_code, self.smo, self.month, self.year, self.cwd)
                else:
                    wc, xreestr= exp_inv(
                        current_app, _sql, mo_code, self.smo, self.month, self.year, pack_type, self.cwd)
                    if csmo and wc > 0:
                        pass
                        #dc= correct_ins(self.smo, self.month, self.year)
        except Exception as e:
            raise e
            return self.exit(self.abort, 500, f"Ошибка сервера: {e}")

        #os.chdir(catalog)
        #sf.cleanup()
        return self.exit(self.resp, xreestr,
            f"Счет {filename}. Записей в счете {rc[0]}, (МЭК {rc[1]}), \
          записей в реестре {wc}.", True)

    def exit(self, fn, *args):
        os.chdir(self.cwd)
        self.sf.cleanup()
        return fn(*args)

    def get(self):
        raise NotImplemented
