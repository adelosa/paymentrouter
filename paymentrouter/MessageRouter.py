import logging
import json
from collections import OrderedDict

LOGGER = logging.getLogger(__name__)


class MessageRouter:

    output_routing_rules = OrderedDict()

    def load_routing_rules(self, json_rules):
        """
        takes string with routing rules config in json format
        :param json_rules: string containing rules in json format
        :return: None
        """
        LOGGER.debug("load_routing_rules")
        self.output_routing_rules = json.loads(json_rules)
        #TODO Validate rules

    def get_message_output_queue(self, message):
        """
        determine the output queue to send message to based on rules
        :param message: standard message data
        :return: queue that message should be routed to
        """
        LOGGER.debug("get_message_output_queue")
        LOGGER.debug("processing tran\n%s", message)

        # evaluate each rule
        for rule_id in sorted(self.output_routing_rules):
            rule_function = self.output_routing_rules[rule_id]['rule_function']
            rule_value = self.output_routing_rules[rule_id]['rule_value']

            LOGGER.debug("Checking rule %s with function %s and value %s",
                         rule_id, rule_function, rule_value)

            # check to see if function pointer available, if not get it
            if not self.output_routing_rules[rule_id].get('rule_function_pointer', None):
                rule_module = self.output_routing_rules[rule_id]['rule_module']
                rule_function = self.output_routing_rules[rule_id]['rule_function']
                mod = __import__(rule_module, fromlist=[rule_function])
                func = getattr(mod, rule_function)
                self.output_routing_rules[rule_id]['rule_function_pointer'] = func

            # execute the rule
            if self.output_routing_rules[rule_id]['rule_function_pointer'](message, rule_value):
                return self.output_routing_rules[rule_id]['queue']

        return "default"  # default queue when no rules match
