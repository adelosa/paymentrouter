from __future__ import absolute_import

import unittest
import logging
import json
from datetime import datetime, date

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from paymentrouter.message_type.json_1 import file_to_dict, dict_to_file, convert_direct_entry_1, date_hook

LOGGER = logging.getLogger(__name__)


class MessageTypeJsonTestCase(unittest.TestCase):

    def test_file_to_dict(self):
        file_content = """
        [
            {"value1": 1, "value2": "two"},
            {"value1": 2, "value2": "three"}
        ]
        """
        file_io = StringIO(file_content)
        vals = file_to_dict(file_io)

        self.assertEqual(2, len(vals))

        expected_vals = [
            {"value1": 1, "value2": "two"},
            {"value1": 2, "value2": "three"}
        ]
        self.assertEqual(expected_vals, vals)

    def test_dict_to_file(self):
        records = [
            {'value1': 4, 'value2': 'two', 'date': datetime(1, 2, 3)},
            {'value1': 5, 'value2': 'three'},
        ]
        file_handle = dict_to_file(records)
        self.assertIsNotNone(file_handle)

        # read the file back to dict using JSON to make sure equal
        output_records = json.load(file_handle, object_hook=date_hook)
        self.assertEqual(records, output_records)

    def test_convert_direct_entry_1(self):
        direct_entry_dict = {
            'record_type': '1',
            'reel_seq_num': '01',
            'name_fin_inst': 'SUN',
            'user_name': 'hello',
            'user_num': '123456',
            'file_desc': 'payroll',
            'date_for_process': '011216',
            'bsb_number': '484-799',
            'account_number': '123456789',
            'indicator': ' ',
            'tran_code': '53',
            'amount': '0000000200',  # $2.00
            'account_title': 'account title',
            'lodgement_ref': 'lodgement ref',
            'trace_bsb_number': '484-799',
            'trace_account_number': '123456789',
            'name_of_remitter': 'MR DELOSA',
            'withholding_tax_amount': '0000000000',
        }
        expected_json_dict = {
            'to_routing': '484-799',
            'to_name': 'account title',
            'to_account': '123456789',
            'from_account': '123456789',
            'amount': 200,
            'from_name': 'MR DELOSA',
            'from_routing': '484-799',
            'tran_type': 'cr',
            'to_description': 'lodgement ref',
            'post_date': date(2016, 12, 1)
        }
        # try a 53 credit de transactions
        self.assertEqual(expected_json_dict, convert_direct_entry_1(direct_entry_dict))

        # try a different credit trancode -- still credit
        direct_entry_dict['tran_code'] = '50'
        self.assertEqual(expected_json_dict, convert_direct_entry_1(direct_entry_dict))

        # try a debit - tc 13
        direct_entry_dict['tran_code'] = '13'
        expected_json_dict['tran_type'] = 'db'
        self.assertEqual(expected_json_dict, convert_direct_entry_1(direct_entry_dict))

if __name__ == '__main__':
    unittest.main()
