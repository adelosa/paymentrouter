"""
dict = {
    'type': 'transfer',
    'amount': 100,
    'amount_exponent': 2,
    'description': 'test transaction',
    'payment_date': '15/03/2016'
    # --- source items
    'source': [{
        'type': 'account',
        'type_routing': '484799',
        'type_key': '123456789',
        'amount': 100,
        'description': 'some description',
    }],
    # --- raw collection format
    'data': {..},
    # --- destination items
    'destination': [{
        'type': 'account',
        'type_routing': '484799',
        'type_key': "123456789",
        'amount': 100,
        'description': 'some description',
    }],
    # --- collection data
    'collection': {
        'source': 'RBA1',
        'format': {
            'type': 'direct_entry',
            'version': 1,
        },
    },
    # --- distribution data
    'distribution': {
        'queue': 'RBA1',
        'format': {
            'type': 'direct_entry',
            'version': 1,
        },
    },
}
"""
from datetime import datetime


class Message(object):
    def __init__(self):
        self.tran_type = ''
        self.tran_amount = 0
        self.tran_amount_exponent = 2
        self.tran_description = ''
        self.source_items = []
        self.destination_items = []
        self.payment_date = datetime.today()
        self.data = {}
        self.collection = {}
        self.distribution = {}

    def add_source_item(self, item_type, type_routing, type_key, amount, description):
        self._add_item(self.source_items, item_type, type_routing, type_key, amount, description)

    def add_destination_item(self, item_type, type_routing, type_key, amount, description):
        self._add_item(self.destination_items, item_type, type_routing, type_key, amount, description)

    def _add_item(self, items, item_type, type_routing, type_key, amount, description):
        item = self.MessageItem()
        item.item_type = item_type
        item.type_routing = type_routing
        item.type_key = type_key
        item.amount = amount
        item.description = description
        items.append(item)

    def get_dict(self):
        val = vars(self)
        val['source_items'] = [vars(item) for item in self.source_items]
        val['destination_items'] = [vars(item) for item in self.destination_items]
        return val

    class MessageItem(object):
        def __init__(self):
            self.item_type = 'account'
            self.type_routing = '484799'
            self.type_key = '123456789'
            self.amount = 100
            self.description = 'some description'
