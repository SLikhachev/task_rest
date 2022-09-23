""" definition of the xml maker class """

from flask_restful import reqparse, inputs
from barsxml.xmlprod.barsxml import BarsXml
from poly.task import RestTask
from poly.utils.fields import month_field

# def requests args
parser = reqparse.RequestParser(bundle_errors=True)
#parser.add_argument('db_srv', type=inputs.url, default=None)
parser.add_argument('mo_code', required=False, default='250796',
    location=('json', 'form'), help='{MO CODE in 250795 format required}')
parser.add_argument('month', type=month_field, required=True,
    location=('json', 'form'), help='{Date in YYYY-MM format required}')
parser.add_argument('type', default='xml',
    location=('json', 'form'), help='{Pack type to make. Default XML}')
parser.add_argument('pack', type=int, default=1, dest='pack_num',
    location=('json', 'form'), help='{Pack number 0-9}' )
# if CHECK is True to check only, else make reestr ignore errors
parser.add_argument('test', type=inputs.boolean, default=False, dest='check',
    location=('json', 'form'), help='{Test flag}')
#if SENT is flase dont setup talon_type=2 as sent talon
parser.add_argument('sent', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Sent flag}')
# if FRESH is false ignore already sent and accepted talons and produce full pack
parser.add_argument('fresh', type=inputs.boolean, default=False,
    location=('json', 'form'), help='{Fresh flag}')


class MakeXml(RestTask):

    def __init__(self):
        super().__init__()


    def post(self):
        try:
            args = parser.parse_args()
        except Exception as exc:
            return self.abort(400, f'Неверный запрос: {exc}')

        try:
            self.year = args['month'][0] #String
            self.base_xml_dir=self.catalog('BASE_XML_DIR')
            # init XmlReporter class
            xml = BarsXml(self,
                args['type'], # String
                args['mo_code'], #String
                args['month'][1], #String
                args['pack_num'] #Int
            )

            # call main method
            _ph, _lm, file, errors = xml.make_xml(
               args['sent'], args['fresh'], args['check']
            )
        except Exception as exc:
            raise exc
            return self.abort(500, exc)

        rslt = f'H записей: {_ph}, L записей: {_lm}. '
        error_msg = ''
        if args['check']: file = ''
        done = True
        if errors > 0:
            error_msg = f'НАЙДЕНО ОШИБОК: {errors}. '
            done = False
            # file -> zip if check is False else error_pack.csv

        return self.resp(file, f'{rslt} {error_msg}', done)
