import unittest
from paymentrouter.MessageRouter import MessageRouter

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def minimum_amount_routing(message, minimum_amount):
    if message['payment_amount'] < minimum_amount:
        return True
    return False


class MessageRouterTestCase(unittest.TestCase):

    router = MessageRouter()
    json_rules = """
    {
        "001_less_than_100" : {
            "rule_module" : "dummy",
            "rule_function" : "minimum_amount_routing",
            "rule_value" : 100,
            "queue" : "less_than_100"
            },
        "002_less_than_200" : {
            "rule_module" : "dummy",
            "rule_function" : "minimum_amount_routing",
            "rule_value" : 200,
            "queue" : "less_than_200"
            },
        "099_bsb_route" : {
            "rule_module" : "paymentrouter.message_type.direct_entry_1",
            "rule_function" : "route_rule_direct_entry_bsb",
            "rule_value" : "^(57993[0-9]|484799)$",
            "queue" : "de_onus"
            }
    }
    """
    router.load_routing_rules(json_rules)
    router.output_routing_rules['001_less_than_100']['rule_function_pointer'] = minimum_amount_routing
    router.output_routing_rules['002_less_than_200']['rule_function_pointer'] = minimum_amount_routing

    def test_less_than_100(self):
        tran = {
            'message_type': 'direct_entry',
            'message_version': 1,
            'payment_amount': 99,
            'bsb_number': '484799',
        }

        selected_queue = self.router.get_message_output_queue(tran)
        self.assertEqual('less_than_100', selected_queue)

    def test_between_100_and_200(self):
        tran = {
            'message_type': 'direct_entry',
            'message_version': 1,
            'payment_amount': 101,
            'bsb_number': '484799',
        }

        selected_queue = self.router.get_message_output_queue(tran)
        self.assertEqual('less_than_200', selected_queue)

    def test_greater_than_200(self):
        tran = {
            'message_type': 'direct_entry',
            'message_version': 1,
            'payment_amount': 201,
            'bsb_number': '484791',
        }

        selected_queue = self.router.get_message_output_queue(tran)
        self.assertEqual('default', selected_queue)

    def test_over_200_onus_tran(self):
        tran = {
            'message_type': 'direct_entry',
            'message_version': 1,
            'payment_amount': 201,
            'bsb_number': '484799',
        }

        selected_queue = self.router.get_message_output_queue(tran)
        self.assertEqual('de_onus', selected_queue)


if __name__ == '__main__':

    unittest.main()
