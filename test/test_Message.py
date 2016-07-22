from __future__ import absolute_import
import unittest
from datetime import datetime

from paymentrouter.Message import Message


class MessageTestCase(unittest.TestCase):

    def test_get_message_data(self):
        message = Message()
        message.add_source_item('account', '484-799', '123456789', 100, 'test transaction')
        message.add_destination_item('account', '484-799', '123456789', 100, 'test transaction')
        message.payment_date = datetime.today()
        message.tran_amount = 100
        message.tran_amount_exponent = 2
        message.tran_type = 'transfer'
        message.tran_description = 'test transaction'

        output = message.get_dict()
        print(output['source_items'])
        print(len(output['source_items']))
        self.assertEqual(1, len(output['source_items']))
