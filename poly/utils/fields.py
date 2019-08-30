from datetime import date


def month_field(val):
    if val != '':
        try:
            dm = [int(s) for s in val.split('-')]
            return dm[0], dm[1]
        except:
            pass
    dm = [int(s) for s in date.today().isoformat().split('-')]
    return dm[0], dm[1]
