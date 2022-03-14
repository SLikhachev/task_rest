
from types import SimpleNamespace as bcfg
from flask_restful import reqparse, inputs
from barsxml.xmlprod.barsxml import BarsXml
from poly.reestr.task import RestTask
from poly.utils.fields import month_field


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
        except Exception as e:
            return self.abort(400, f'{e}')
        cfg = bcfg(
            SQL=self.sql_provider, # String
            SQL_SRV=self.sql_srv, # dict
            YEAR = args['month'][0], #String
            BASE_XML_DIR=self.catalog('BASE_XML_DIR')
        )
        try:
            xml = BarsXml(
                cfg, args['type'], # String
                args['mo_code'], #String
                args['month'][1], #String
                args['pack_num'] #Int
            )
            ph, lm, file, errors = xml.make_xml(
               args['sent'], args['fresh'], args['check']
            )
        except Exception as e:
            #raise e
            return self.abort(500, e)

        z= f'H записей: {ph}, L записей: {lm}. '
        e = ''
        if args['check']: file = ''
        done = True
        if errors > 0:
            e = f'НАЙДЕНО ОШИБОК: {errors}. '
            done = False
            # file -> zip if check is False else error_pack.csv

        return self.resp(file, f'{z} {e}', done)
