from datetime import date


def month_field(val: str) -> tuple:
    if val != '':
        try:
            dm = [s for s in val.split('-')]
            return dm[0], dm[1]
        except:
            pass
    dm = [s for s in date.today().isoformat().split('-')]
    return dm[0], dm[1]


def pack_field(val: int) -> str:
    if val < 1 or val > 99:
        return '01'
    if val < 10:
        return f'0{val}'
    return str(val)