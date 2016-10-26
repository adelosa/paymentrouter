"""
generic format used for storing transactions in the warehouse

dict = {
    'payment_date': '15/03/2016'
    'status': 'ready'
    # --- collection data
    'collection': {
        'source': 'RBA1',
        'format': {
            'name': 'direct_entry',
            'version': 1,
        },
        'data': {...},
    },

    # --- distribution data
    'distribution': {
        'queue': 'RBA1',
        'format': {
            'name': 'direct_entry',
            'version': 1,
        },
        'data': {...}  # if different from collection
    },
}
"""
from datetime import datetime
from mongoengine import (
    StringField, IntField, Document, EmbeddedDocument, EmbeddedDocumentField, DictField,
    DateTimeField,
)


class PPrintMixin(object):
    def __str__(self):
        return '<{}: id={!r}>'.format(type(self).__name__, self.id)

    def __repr__(self):
        attrs = []
        for name in self._fields.keys():
            value = getattr(self, name)
            if isinstance(value, (Document, EmbeddedDocument)):
                attrs.append('\n    {} = {!s},'.format(name, value))
            else:
                attrs.append('\n    {} = {!r},'.format(name, value))
        return '<{}: {}\n>'.format(type(self).__name__, ''.join(attrs))


class MessageFormat(EmbeddedDocument):
    name = StringField()
    version = IntField()


class MessageCollection(EmbeddedDocument):
    source = StringField()
    format = EmbeddedDocumentField(MessageFormat)
    data = DictField()


class MessageDistribution(EmbeddedDocument):
    queue = StringField()
    format = EmbeddedDocumentField(MessageFormat)
    data = DictField()


class Message(PPrintMixin, Document):
    payment_date = DateTimeField()
    collection = EmbeddedDocumentField(MessageCollection)
    distribution = EmbeddedDocumentField(MessageDistribution)
    status = StringField(regex=r"^(ready|done|error)$")


def build_message(template=None, **kwargs):
    """
    factory method to create message objects
    :param template: dict containing default values to use where no kwarg provided
    :param kwargs: dict containing values to set
    :return: Message object
    """
    # set default template
    defaults = {
        'source': 'NoSource',
        'format_name': 'NoFormat',
        'format_version': 1,
        'data': {},
        'queue': 'default',
        'status': 'ready',
        'payment_date': datetime.today().date()
    }
    if template is None:
        template = dict()

    def get_value(value):
        return kwargs.get(value, template.get(value, defaults[value]))

    data = get_value('data')
    return Message(
        collection=MessageCollection(
            source=get_value('source'),
            format=MessageFormat(
                name=get_value('format_name'),
                version=get_value('format_version')
            ),
            data=data
        ),
        distribution=MessageDistribution(
            queue=get_value('queue')
        ),
        payment_date=get_value('payment_date'),
        status=get_value('status')
    )
