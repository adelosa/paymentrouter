import json
from datetime import datetime, date
from pprint import pformat

from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base(object):
    def __repr__(self):
        return '<{}: {}\n>'.format(type(self).__name__, pformat(vars(self)))


def _default(val):
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    raise TypeError("got type {}".format(type(val)))


def dumps(d):
    return json.dumps(d, default=_default)
