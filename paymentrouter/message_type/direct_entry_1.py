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
        'amount': '0000000200',  # $2.00
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

REGEX_DE_HEADER = (
    r"^(?P<record_type>0) {17}"
    r"(?P<reel_seq_num>\d{2})"
    r"(?P<name_fin_inst>.{3}).{7}"
    r"(?P<user_name>.{26})"
    r"(?P<user_num>\d{6})"
    r"(?P<file_desc>.{12})"
    r"(?P<date_for_process>\d{6}).{40}$")

REGEX_DE_DETAIL = (
    r"^(?P<record_type>[1-3])"
    r"(?P<bsb_number>\d{3}-\d{3})"
    r"(?P<account_number>\d{9})"
    r"(?P<indicator>.)"
    r"(?P<tran_code>\d{2})"
    r"(?P<amount>\d{10})"
    r"(?P<account_title>.{32})"
    r"(?P<lodgement_ref>.{18})"
    r"(?P<trace_bsb_number>\d{3}-\d{3})"
    r"(?P<trace_account_number>\d{9})"
    r"(?P<name_of_remitter>.{16})"
    r"(?P<withholding_tax_amount>\d{8})$")


def file_to_dict(file_handle):
    """
    convert file to list of dicts, each dict representing a record.
    :param file_handle:
    :return:
    """
    file_contents = file_handle.readlines()
    LOGGER.debug("file contents \n%s", file_contents)
    output_records = []
    header = None
    last_record_type = 'S'  # start new set

    for file_contents_line in file_contents:

        record_type = file_contents_line[:1]
        LOGGER.debug("record_type=%s", record_type)

        if record_type == '0' and last_record_type in ('S', '7'):

            # validate/get the header record fields
            header = re.match(REGEX_DE_HEADER, file_contents_line)
            if not header:
                raise Exception('Invalid record format - de header')

        elif record_type in ('1', '2', '3') and last_record_type in ('0', '1', '2', '3'):

            # validate/get the detail record fields
            detail = re.match(REGEX_DE_DETAIL, file_contents_line)
            if not detail:
                raise Exception('Invalid record format - de detail')

            # build transaction record
            output_record = build_transaction(header, detail)

            # add message to output list
            output_records.append(output_record)

        elif record_type == '7' and last_record_type in ('1', '2', '3'):
            pass
        else:
            raise Exception('Invalid record type - record_type=[{}], last_record_type=[{}]'.format(record_type, last_record_type))

        last_record_type = record_type

    return output_records


def build_transaction(header, detail):

    message = Message()

    message.data = header.groupdict()
    message.data.update(detail.groupdict())

    message.collection['format'] = {'type': 'direct_entry', 'version': 1}
    message.tran_type = 'transfer'
    message.tran_amount = int(message.data['amount'])
    message.tran_amount_exponent = 2
    message.tran_description = 'direct entry'
    message.payment_date = datetime.today()

    message.add_source_item(
        'account',
        message.data['bsb_number'],
        message.data['account_number'],
        int(message.data['amount']),
        message.data['lodgement_ref']
    )

    message.add_destination_item(
        'account',
        message.data['trace_bsb_number'],
        message.data['trace_account_number'],
        int(message.data['amount']),
        message.data['name_of_remitter']
    )

    return message.get_dict()


def is_message_ok(message_format):
    """
    check that message type and version is correct
    """
    LOGGER.debug(message_format)
    if (message_format['type'] == 'direct_entry' and
       message_format['version'] == 1):
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
