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
    file_contents = file_handle.readlines()
    output_records = []

    for file_contents_line in file_contents:
        record_type = file_contents_line[:1]
        if record_type == '0':
            header = slices(file_contents_line, 18, 2, 3, 7, 26, 6, 12, 6)
        if record_type in ('1', '2', '3'):
            detail = slices(file_contents_line, 1, 7, 9, 1, 2, 10, 32, 18, 7, 9, 16, 8)
            transaction = {
                'message_type': 'direct_entry',
                'message_version': 1,
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
            output_records.append(transaction)
        if record_type == '7':
            pass

    return output_records


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


def slices(s, *args):
    position = 0
    return_vals = []
    for length in args:
        return_vals.append(s[position:position + length])
        position += length
    return return_vals
