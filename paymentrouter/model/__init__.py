import json
from datetime import datetime, date

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def _default(val):
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    raise TypeError("got type {}".format(type(val)))


def dumps(d):
    return json.dumps(d, default=_default)
