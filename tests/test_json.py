from __future__ import absolute_import
import unittest
import logging
import json

from io import StringIO

from paymentrouter.message_type.json_1 import file_to_dict, dict_to_file

LOGGER = logging.getLogger(__name__)


class MessageTypeJsonTestCase(unittest.TestCase):

    def test_file_to_dict(self):
        file_content = """
        [
            {"value1": 1, "value2": "two"},
            {"value1": 2, "value2": "three"}
        ]
        """
        with StringIO(file_content) as file_io:
            vals = file_to_dict(file_io)

        self.assertEqual(2, len(vals))

        expected_vals = [
            {"value1": 1, "value2": "two"},
            {"value1": 2, "value2": "three"}
        ]
        self.assertEqual(expected_vals, vals)

    def test_dict_to_file(self):
        records = [
            {'value1': 4, 'value2': 'two'},
            {'value1': 5, 'value2': 'three'},
        ]
        file_handle = dict_to_file(records)
        self.assertIsNotNone(file_handle)

        # read the file back to dict using JSON to make sure equal
        output_records = json.load(file_handle)
        self.assertEqual(records, output_records)


if __name__ == '__main__':
    unittest.main()
