from __future__ import absolute_import
import unittest
import logging

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

        print(str(len(vals)) + "\n" + str(vals))

    def test_dict_to_file(self):
        record = [
            {'value1': 1, 'value2': 'two'},
            {'value1': 2, 'value2': 'three'},
        ]
        file_handle = dict_to_file(record)
        assert file_handle is not None
        output = file_handle.readlines()
        print("1>>>>>>>>>>" + str(len(output)))
        for line in output:
            print("2>>>>>>>>>>" + str(line))

    def test_values(self):
        print(type('value'))
        print(type(123))
        print(type(123.456))


if __name__ == '__main__':
    unittest.main()
