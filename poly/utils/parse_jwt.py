""" parse JWT token """

import jwt


def parse_jwt_token(header, secret):
    """ parse """
    _jw = header.strip()
    key = _jw.split(' ') # list of 2 els: 1st "Bearer " 2nd is jwt key
    #print(key)
    if len(key) < 2 or len(key[1]) < 2:
        return 401, "Bad Authorization Bearer's header", ''
    try:
        payload = jwt.decode(key[1], secret, algorithms=["HS256"])
        role = payload['role']
        user=payload['user']
    except jwt.DecodeError:
        return 401, 'Invalid token', ''
    except jwt.ExpiredSignatureError:
        return 401, 'Token has expired', ''
    except KeyError:
        return 401, 'Token payload invalid', ''

    return 200, role, user