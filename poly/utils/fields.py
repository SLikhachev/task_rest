
from typing import Tuple
from datetime import date


def month_field(date_str: str) -> Tuple[str, str]:
    """
    get (year, month) strings from date string
    @params
        :val: str - wait string of date format as 'YYYY-MM-DD' (ISO format: 2023-01-23)
    returns
        tuple('2023', '01')
    """

    if date_str != '':
        try:
            dm = list(date_str.split('-'))
            assert len(dm[0]) == 4 and dm[0].startswith('20'), f"Поле год не соответвует формату: {dm[0]}"
            assert int(dm[1]) in range(1,13), f"Поле месяц не соответвует формату: {dm[1]}"
            return dm[0], dm[1]
        except Exception:
            pass
    # return current YYYY-MM
    dm = list(date.today().isoformat().split('-'))
    return dm[0], dm[1]


def pack_field(val: int) -> str:
    """ Package number validator
    """
    if val < 1 or val > 99:
        return '01'
    if val < 10:
        return f'0{val}'
    return str(val)