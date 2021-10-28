import os
from datetime import datetime
#from tempfile import TemporaryFile as stmp
from tempfile import TemporaryDirectory as stmp
from flask_restful import reqparse, abort
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

    def __init__(self):
        super().__init__()

    def post(self):
        try:
            args = parser.parse_args()
        except Exception as e:
            current_app.logger.debug(f'{e}')
            return self.abort(400, f'{e}')

        file = args['files'][0] # only first FileStorage
        filename = secure_filename(file.filename)
        if not allowed_file( filename, current_app.config ) or not filename.endswith('.xml'):
            return self.abort(400, f"Допустимое расширение имени файла .xml {filename}")

        _, _, ar, _ = self.parse_xml_name(filename)

        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')
        sf= stmp(dir=catalog)
        up_file = os.path.join(sf.name, filename)
        file.save(up_file)

        try:
            rc= geterrs(up_file, self.sql_srv, ar, ('824',), 'ignore')
        except Exception as e:
            current_app.logger.debug(e)
            sf.cleanup()
            return self.abort(500, f"Ошибка при обработке файла {filename}: {e}")

        sf.cleanup()
        return self.resp(filename,
            f"Файл ошибок: {filename} Записей считано {rc}", True)

    def get(self):

        with SqlProvider(self.sql_srv) as db:
            qurs= db.cursor()
            qurs.execute(config.COUNT_ERRORS)
            rc= qurs.fetchone()
        
            if not bool(rc[0]):
                return self.resp('', "Нет принятых ошибок", False)
        
            catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reestr', 'vmx')
            df= str(datetime.now()).split(' ')[0]
            filename= f"ERR_{df}_{get_name_tail(5)}.csv"
            _file = os.path.join(catalog, filename)
            try:
                qurs.execute(config.TO_CSV % _file)
            except Exception as e:
                current_app.logger.debug(e)
                return self.abort(500, f"Не удалось сформировать файл ошибокю {e}")

        return self.resp(_file, "Посдение ошибки", True)
