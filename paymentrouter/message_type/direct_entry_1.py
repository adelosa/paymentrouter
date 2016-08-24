"""
direct entry format

Dictionary format for direct_entry
----------------------------------
{
    'version': 1,
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
    'withholding_tax_amount': '00000000',
}
"""
import os
import logging
import re
from io import StringIO


LOGGER = logging.getLogger(__name__)

REGEX_DE_HEADER = (
    r'^(?P<record_type>0) {17}'
    r'(?P<reel_seq_num>\d{2})'
    r'(?P<name_fin_inst>.{3}).{7}'
    r'(?P<user_name>.{26})'
    r'(?P<user_num>\d{6})'
    r'(?P<file_desc>.{12})'
    r'(?P<date_for_process>\d{6}).{40}$')

REGEX_DE_DETAIL = (
    r'^(?P<record_type>[1-3])'
    r'(?P<bsb_number>\d{3}-\d{3})'
    r'(?P<account_number>\d{9})'
    r'(?P<indicator>.)'
    r'(?P<tran_code>\d{2})'
    r'(?P<amount>\d{10})'
    r'(?P<account_title>.{32})'
    r'(?P<lodgement_ref>.{18})'
    r'(?P<trace_bsb_number>\d{3}-\d{3})'
    r'(?P<trace_account_number>\d{9})'
    r'(?P<name_of_remitter>.{16})'
    r'(?P<withholding_tax_amount>\d{8})$')


def file_to_dict(file_handle):
    """
    convert file to list of dicts, each dict representing a record.
    :param file_handle:
    :return:
    """
    file_contents = file_handle.readlines()
    LOGGER.debug('file contents \n%s', file_contents)
    output_records = []
    header = None
    last_record_type = 'S'  # start new set

    for file_contents_line in file_contents:

        record_type = file_contents_line[:1]
        LOGGER.debug('record_type=%s', record_type)

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
            LOGGER.debug("Creating OUTPUT DICT Direct entry\n%s\n%s", header.groupdict(), detail.groupdict())
            output_record = {'version': 1}
            output_record.update(header.groupdict())
            output_record.update(detail.groupdict())
            LOGGER.debug("%s", output_record)

            # add message to output list
            output_records.append(output_record)

        elif record_type == '7' and last_record_type in ('1', '2', '3'):
            pass
        else:
            raise Exception('Invalid record type - record_type=[{}], last_record_type=[{}]'.format(record_type, last_record_type))

        last_record_type = record_type

    return output_records

TOTAL_DEBITS = 0
TOTAL_CREDITS = 1
TOTAL_ITEMS = 2


def dict_to_file(data):
    """
    creates file format from transaction records
    :param data: list of dicts
    :return: file stream
    """
    def get_trailer(trailer_totals):
        trailer_format = (
            u'7' +
            u'999-999' +
            u' ' * 12 +
            u'{net_total:010}' +
            u'{credit_total:010}' +
            u'{debit_total:010}' +
            u' ' * 24 +
            u'{count_trans:06}' +
            u' ' * 40
        )
        return trailer_format.format(
            net_total=abs(trailer_totals[TOTAL_CREDITS]-trailer_totals[TOTAL_DEBITS]),
            credit_total=trailer_totals[TOTAL_CREDITS],
            debit_total=trailer_totals[TOTAL_DEBITS],
            count_trans=trailer_totals[TOTAL_ITEMS]
        )

    record_format = (
        u'0' +
        u' ' * 17 +
        u'{reel_seq_num:2.2}' +
        u'{name_fin_inst:3}' +
        u' ' * 7 +
        u'{user_name:26.26}' +
        u'{user_num:6.6}' +
        u'{file_desc:12.12}' +
        u'{date_for_process:6.6}' +
        u' ' * 40 +
        u'{record_type:1.1}' +
        u'{bsb_number:7.7}' +
        u'{account_number:9.9}' +
        u'{indicator:1.1}' +
        u'{tran_code:2.2}' +
        u'{amount:10.10}' +
        u'{account_title:32.32}' +
        u'{lodgement_ref:18.18}' +
        u'{trace_bsb_number:7.7}' +
        u'{trace_account_number:9.9}' +
        u'{name_of_remitter:16.16}' +
        u'{withholding_tax_amount:8.8}'
    )

    LOGGER.debug('record_format={}'.format(record_format))
    flat_trans = sorted([(record_format.format(**tran), tran) for tran in data])

    # remove duplicate headers and accumulate for trailer
    last_header = ''
    output_list = []
    totals = [0, 0, 0]

    for tran, data in flat_trans:
        if last_header != tran[:120]:
            if len(output_list) != 0:
                output_list.append(get_trailer(totals))
                totals = [0, 0, 0]

            output_list.append(tran[:120])
            last_header = tran[:120]

        if data['tran_code'] == u'13':
            totals[TOTAL_CREDITS] += int(data['amount'])
        else:
            totals[TOTAL_DEBITS] += int(data['amount'])
        totals[TOTAL_ITEMS] += 1
        output_list.append(tran[120:])

    output_list.append(get_trailer(totals))

    # add line endings
    output_list = [line + os.linesep for line in output_list]

    # add to stream
    output_stream = StringIO()
    output_stream.writelines(output_list)
    output_stream.seek(0)

    return output_stream


def is_message_version_ok(message):
    """
    check that message type and version is correct
    """
    LOGGER.debug(message)
    if message.get('version', 0) == 1:
        return True
    return False


def route_rule_direct_entry_bsb(message, bsb_regex):
    """
    check for BSB that matches regex provided
    :param message: the direct_entry message type
    :param bsb_regex: regex to locate
    :return: Boolean - True if rule matched
    """
    LOGGER.debug('route_rule_direct_entry_bsb:%s', message)
    if not is_message_version_ok(message):
        LOGGER.warn('Rule not processed as message wrong format or version')
        return False

    if re.match(bsb_regex, message['bsb_number']):
        return True
    return False
