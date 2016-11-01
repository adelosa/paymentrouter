"""
json format

dictionary format for json files

[{
    'post_date': date(1,1,2000),
    'tran_type': 'cr', # or 'db'
    'amount': 1000,   # No decimals - in cents
    'to_account': '123456789',
    'to_routing': '484-799',
    'to_name': 'joe bloggs',
    'to_description': 'fee for lawn mowing',
    'from_account': '987654321',
    'from_routing': '111-222',
    'from_name': 'jack black'
},
{
    # next record
}]
"""
import logging
import json
from datetime import datetime, date

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

LOGGER = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def date_hook(json_dict):
    LOGGER.debug("date_hook called with json_dict=\n%s", json_dict)
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except:
            pass
    return json_dict


def file_to_dict(file_handle):
    """
    convert file to list of dicts, each dict representing a record.
    :param file_handle:
    :return:
    """
    output_dict = json.load(file_handle, object_hook=date_hook)

    return output_dict


def dict_to_file(data):
    """
    creates file format from transaction records
    :param data: list of dicts
    :return: file stream
    """
    outfile = StringIO()
    json.dump(data, outfile, cls=DateTimeEncoder, indent=4, separators=(',', ': '))
    outfile.seek(0)
    return outfile


def convert_direct_entry_1(direct_entry):
    """
    converts direct_entry_1 dict to json dict format
    :param direct_entry: direct_entry_1 format dict
    :return: json_1 format dict
    """
    date_post = datetime.strptime(direct_entry['date_for_process'], '%d%m%y').date()
    return {
        'tran_type': 'db' if direct_entry['tran_code'] == '13' else 'cr',
        'amount': int(direct_entry['amount']),   # No decimals - in cents
        'to_account': direct_entry['account_number'],
        'to_routing': direct_entry['bsb_number'],
        'to_name': direct_entry['account_title'],
        'to_description': direct_entry['lodgement_ref'],
        'from_account': direct_entry['trace_account_number'],
        'from_routing': direct_entry['trace_bsb_number'],
        'from_name': direct_entry['name_of_remitter'],
        'post_date': date_post,
    }
