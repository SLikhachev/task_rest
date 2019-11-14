
import traceback
import linecache
import sys

class TagError(Exception):
    def __init__(self, msg, original_exception):
        super(TagError, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception

def printTraceback():
    return traceback.format_exc()

def printException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
