from datetime import datetime
from pprint import pformat

import enum

from sqlalchemy import Column, Integer, String, SmallInteger, Date, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TransactionStatus(enum.Enum):
    ready = 'READY'
    processed = 'PROCESSED'
    failed = 'FAILED'


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True)
    submission_id = Column(String)
    status = Column(Enum(TransactionStatus))
    collection_format_name = Column(String(20))
    collection_format_version = Column(SmallInteger)
    collection_data = Column(JSONB)
    collection_datetime = Column(DateTime)
    queue = Column(String)
    distribution_format_name = Column(String(20))
    distribution_format_version = Column(SmallInteger)
    distribution_data = Column(JSONB)
    distribution_date = Column(Date)

    def __repr__(self):
        return '<{}: {}\n>'.format(type(self).__name__, pformat(vars(self)))


def build_message(template=None, **kwargs):
    """
    factory method to create transaction objects
    :param template: dict containing default values to use where no kwarg provided
    :param kwargs: dict containing values to set
    :return: Message object
    """
    # set default template
    defaults = {
        'submission_id': 1,
        'status': TransactionStatus.ready,
        'collection_format_name': 'NoFormat',
        'collection_format_version': 1,
        'collection_data': {},
        'collection_datetime': datetime.today().date(),
        'queue': 'default',
    }
    if template is None:
        template = dict()

    def get_value(value):
        return kwargs.get(value, template.get(value, defaults[value]))

    return Transaction(
        submission_id=get_value('submission_id'),
        status=get_value('status'),
        collection_format_name=get_value('collection_format_name'),
        collection_format_version=get_value('collection_format_version'),
        collection_data=get_value('collection_data'),
        collection_datetime=get_value('collection_datetime'),
        queue=get_value('queue')
    )
