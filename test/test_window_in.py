import unittest
import mock
from paymentrouter.cli.window_in import convert_input, route_items, write_to_mongo


def file_to_dict(file_handle):
    file_contents = file_handle.read()
    return {'id': 1, 'value': file_contents}


def dummy_rule(message, value):
    if message['value'] == 1:
        return True
    return False


class WindowInTestCase(unittest.TestCase):

    @mock.patch('paymentrouter.message_type.direct_entry_1.file_to_dict', side_effect=file_to_dict)
    def test_convert_input(self, mock_message_type):
        with mock.patch('builtins.open', mock.mock_open(read_data='test')):
            with open('/dev/null') as file_handle:
                output = convert_input({'name': 'direct_entry', 'version': 1}, file_handle)
        self.assertEqual(output, {'id': 1, 'value': 'test'})


    @mock.patch(
        'paymentrouter.message_type.direct_entry_1.route_rule_direct_entry_bsb',
        side_effect=dummy_rule)
    def test_route_items(self, mock_rule):
        file_dict = [
            {'id': 1, 'value': 1},
            {'id': 2, 'value': 2},
            {'id': 3, 'value': 1},
        ]
        routing = {
            "rule1": {
                "rule_module": "paymentrouter.message_type.direct_entry_1",
                "rule_function": "route_rule_direct_entry_bsb",
                "rule_value": 1,
                "queue": "queue_1"
            },
        }
        route_items(file_dict, routing)
        self.assertEqual(len(file_dict), 3)
        print(file_dict)
        for item in file_dict:
            self.assertIn('id', item)
            self.assertIn('queue', item)
            if item['id'] in (1, 3):
                self.assertEqual(item['queue'], 'queue_1')
            else:
                self.assertEqual(item['queue'], 'default')

    def test_write_to_mongo(self):
        file_dict = [
            {'id': 1, 'value': 1, 'queue': 'one'},
            {'id': 2, 'value': 2, 'queue': 'two'},
            {'id': 3, 'value': 1, 'queue': 'one'},
        ]
        write_to_mongo(file_dict, '192.168.99.100', 'test')
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
