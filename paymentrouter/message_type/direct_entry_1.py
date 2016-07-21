"""
direct entry format

Dictionary format for direct_entry
----------------------------------
{
    'data': {
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
        'amount': 200,  # $2.00
        'account_title': 'account title',
        'lodgement_ref': 'lodgement ref',
        'trace_bsb_number': '484-799',
        'trace_account_number': '123456789',
        'name_of_remitter': 'MR DELOSA',
        'amount_of_withholding_tax': '0000000000',
        },
}
"""
import logging
import re
from datetime import datetime

from paymentrouter.Message import Message


LOGGER = logging.getLogger(__name__)


def file_to_dict(file_handle):
    """
    convert file to list of dicts, each dict representing a record.
    :param file_handle:
    :return:
    """
    file_contents = file_handle.readlines()
    LOGGER.debug("file contents \n%s", file_contents)
    output_records = []

    for file_contents_line in file_contents:
        record_type = file_contents_line[:1]
        LOGGER.debug("record_type=%s", record_type)
        if record_type == '0':
            header = slices(file_contents_line, 18, 2, 3, 7, 26, 6, 12, 6)
        if record_type in ('1', '2', '3'):
            detail = slices(file_contents_line, 1, 7, 9, 1, 2, 10, 32, 18, 7, 9, 16, 8)
            message = Message()
            message.collection['format'] = {'type': 'direct_entry', 'version': 1}
            message.data = {
                'record_type': record_type,
                'reel_seq_num': header[1],
                'name_fin_inst': header[2],
                'user_name': header[4],
                'user_num': header[5],
                'file_desc': header[6],
                'date_for_process': header[7],
                'bsb_number': detail[1],
                'account_number': detail[2],
                'indicator': detail[3],
                'tran_code': detail[4],
                'amount': int(detail[5]),
                'account_title': detail[6],
                'lodgement_ref': detail[7],
                'trace_bsb_number': detail[8],
                'trace_account_number': detail[9],
                'name_of_remitter': detail[10],
                'amount_of_withholding_tax': detail[11]
            }
            LOGGER.debug(message.get_dict())
            message.tran_type = 'transfer'
            message.tran_amount = message.data['amount']
            message.tran_amount_exponent = 2
            message.tran_description = 'yo'
            message.payment_date = datetime.today()
            message.add_source_item(
                'account',
                message.data['bsb_number'],
                message.data['account_number'],
                message.data['amount'],
                message.data['lodgement_ref']
            )
            message.add_destination_item(
                'account',
                message.data['trace_bsb_number'],
                message.data['trace_account_number'],
                message.data['amount'],
                message.data['name_of_remitter']
            )

            output_records.append(message.get_dict())
        if record_type == '7':
            pass

    return output_records


def is_message_ok(message_format):
    """
    check that message type and version is correct
    """
    LOGGER.debug(message_format)
    if (message_format['version'] == 1 and
       message_format['type'] == 'direct_entry'):
        return True
    return False


def route_rule_direct_entry_bsb(message, bsb_regex):
    """
    check for BSB that matches regex provided
    :param message: the direct_entry message type
    :param bsb_regex: regex to locate
    :return: Boolean - True if rule matched
    """
    LOGGER.debug("route_rule_direct_entry_bsb:%s", message)
    if not is_message_ok(message['collection']['format']):
        LOGGER.warn("Rule not processed as message wrong format or version")
        return False

    if re.match(bsb_regex, message['data']['bsb_number']):
        return True
    return False


def slices(s, *args):
    position = 0
    return_vals = []
    for length in args:
        return_vals.append(s[position:position + length])
        position += length
    return return_vals
