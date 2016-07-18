"""
direct entry format

Dictionary format for direct_entry
----------------------------------
{
    'message_type': 'direct_entry',
    'message_version': 1,
    'trancode': 53,
    'transaction_amount': 100,
    'bsb_number': '484799',
    'account_number': '123456789',
    'trace_bsb_number': '484799',
    'trace_account_number': '123456789',
    'reference': '123456789012345678',
    'to_account_name': 'mr anthony d',
    'from_account_name': 'banktek systems',
}

file_to_dict(filename)
read file and convert to [{dict}] as above


"""
import logging
import re


LOGGER = logging.getLogger(__name__)


def file_to_dict(file_handle):
    """
    convert file to list of dicts, each dict representing a record.
    :param file_handle:
    :return:
    """
    file_contents = file_handle.read()
    return [
        {'id': 1,
         'value': file_contents,
         "message_version": 1,
         "message_type": 'direct_entry',
         "bsb_number": '484799'
         }
    ]


def is_message_ok(message):
    """
    check that message type and version is correct
    :param message:
    :return:
    """
    if message['message_version'] == 1 and message['message_type'] == 'direct_entry':
        return True
    return False


def route_rule_direct_entry_bsb(message, bsb_regex):
    """
    check for BSB that matches regex provided
    :param message: the direct_entry message type
    :param bsb_regex: regex to locate
    :return: Boolean - True if rule matched
    """
    if not is_message_ok(message):
        LOGGER.warn("Rule not processed as message wrong format or version")
        return False

    if re.match(bsb_regex, message['bsb_number']):
        return True
    return False
