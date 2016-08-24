"""
MessageRouter
-------------
takes a message and routes it using rules to required destination
rules are executed in order based on rule name
rule_module is optional.

json_config format
{
    "rule1" : {
        "rule_function" : "minimum_amount_routing",
        "rule_value" : 100,
        "queue" : "less_than_100"
    },
    "rule2" : {
        "rule_module" : "mymodule.folder.module_name'
        "rule_function" : "minimum_amount_routing",
        "rule_value" : 200,
        "queue" : "less_than_200"
    }
}
"""
import logging
import json
from collections import OrderedDict

LOGGER = logging.getLogger(__name__)


class MessageRouter:
    """
    determine queue to route message to based on message format and rules
    """

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

    def get_message_output_queue(self, message, default_rule_module=None):
        """
        determine the output queue to send message to based on rules
        :param message: standard message data
        :param default_rule_module: use as module when not provided
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
                rule_module = self.output_routing_rules[rule_id].get(
                    'rule_module', default_rule_module
                )
                rule_function = self.output_routing_rules[rule_id]['rule_function']
                mod = __import__(rule_module, fromlist=[rule_function])
                func = getattr(mod, rule_function)
                self.output_routing_rules[rule_id]['rule_function_pointer'] = func

            # execute the rule
            if self.output_routing_rules[rule_id]['rule_function_pointer'](message, rule_value):
                return self.output_routing_rules[rule_id]['queue']

        return "default"  # default queue when no rules match
