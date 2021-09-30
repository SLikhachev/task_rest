from functools import wraps
import requests
from flask import current_app
from flask_restful import abort


def check_db_srv(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        db_srv = self.db_srv if self.db_srv else self.args['db_srv']
        if not db_srv:
            msg = f"DB server not defined"
            current_app.logger.debug(msg)
            abort(404, message=msg)
        try:
            requests.options(f'{db_srv}/doctor', timeout=0.5)
        except requests.exceptions.Timeout as e:
                current_app.logger.debug(e)
                abort(404, message=f"DB server {db_srv} timeout")
        current_app.config['DB_SRV'] = db_srv
        self.db_srv = db_srv
        return func(self, *args, **kwargs)
    return wrapper
