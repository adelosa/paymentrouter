"""
json format

dictionary format for json files

[{
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
from io import StringIO


LOGGER = logging.getLogger(__name__)


def file_to_dict(file_handle):
    """
    convert file to list of dicts, each dict representing a record.
    :param file_handle:
    :return:
    """
    return json.load(file_handle)


def dict_to_file(data):
    """
    creates file format from transaction records
    :param data: list of dicts
    :return: file stream
    """
    outfile = StringIO()
    json.dump(data, outfile)
    outfile.seek(0)
    return outfile
