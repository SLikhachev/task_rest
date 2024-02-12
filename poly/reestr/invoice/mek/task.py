""" mek task API handlers """

import os
import functools

from flask_restful import reqparse
from flask import current_app


from poly.task import RestTask
from poly.utils.fields import month_field
from poly.reestr.invoice.mek.move_mek import CarryMek


parser = reqparse.RequestParser()
parser.add_argument('month', type=month_field, required=True,
    location=('form', 'values'), help='{From source month date in YYYY-MM format required}')
parser.add_argument('target', type=month_field, required=True,
    location=('form', 'values'), help='{To target month date in YYYY-MM format required}')

def check_meks(method):
    """ Check have a meks
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            self.parse_dates()
        except Exception as exc:
            #raise exc
            return self.abort(400, exc)

        self.mek = CarryMek(self)
        # rerturn non empty string if meks not found
        meks = self.mek.check_meks()
        if meks:
            return self.resp('',meks, False)

        return method(self, *args, **kwargs)
    return wrapper


class MoveMek(RestTask):
    """ Move MEK records task class """

    def __init__(self):
        super().__init__()
        # self.this_year = from base class
        # self.mo_code = current_app.config['STUB_MO_CODE']
        self.from_year = None
        self.to_year = None
        self.from_month = None
        self.to_month = None
        self._year = None
        self.test = os.getenv('TEST')
        self.mek = None
        self.mo_code = current_app.config.get('STUB_MO_CODE', '000000')

    def month_to_int(self, month: str) -> int:
        """ month string '01' - '12' to int """
        try:
            m = abs(int(month))
            if m == 0 or m > 12:
                return 1
        except ValueError:
            return 1
        return m

    def parse_dates(self):
        """ parse request dates """
        args = parser.parse_args()
        self.from_year, self.from_month = args['month']
        self.to_year, self.to_month= args['target']
        self._year = int(self.from_year[2:])
        self.from_year = int(self.from_year)
        self.to_year = int(self.to_year)
        self.from_month= self.month_to_int(self.from_month)
        self.to_month = self.month_to_int(self.to_month)
        #print(self.from_year, self.from_month, self.to_month)

    # export to csv file task
    @check_meks
    def get(self):
        """ extract the MEKs records from talonz_clin and output as
            CSV file in the GET request
        """
        try:
            file, msg = self.mek.meks_to_csv()
            return self.resp(file, msg, True)
        except Exception as exc:
            raise exc
            #return self.abort(500, f'Ошибка формирования файла МЭК')

    # move mek
    @check_meks
    def post(self):
        """ move the MEKs to the next month task in the POST request
            checks the correctness of the forms data to continue
        """
        msg = self.mek.check_dates()
        if msg:
            return self.abort(400, msg)

        try:
            msg = self.mek.move_mek()
            return self.resp('', msg, True)
        except Exception as exc:
            raise exc
            #return self.abort(500, f'Ошибка переноса МЭК {exc}')
