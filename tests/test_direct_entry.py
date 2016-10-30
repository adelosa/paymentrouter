from __future__ import absolute_import
import unittest
import logging
import copy
import re
from io import StringIO
from datetime import date

from paymentrouter.message_type.direct_entry_1 import file_to_dict, dict_to_file, convert_json_1

LOGGER = logging.getLogger(__name__)


class MessageTypeDirectEntryTestCase(unittest.TestCase):
    def test_file_to_dict_multi_header_ok(self):
        file_content = (
            u"0                 01SUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"1484-799123456789 530000000123ACCOUNT TITLE2------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"1484-799123456789 530000000123ACCOUNT TITLE3------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
            u"0                 01SUN       MRS NEWMAN PTY LTD--------123456SUPER PAYMEN011216                                        \n"
            u"1484-799123456789 530000000123ACCOUNT TITLE4------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"1484-799123456789 530000000123ACCOUNT TITLE5------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"1484-799123456789 530000000123ACCOUNT TITLE6------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        "
        )
        with StringIO(file_content) as file_io:
            vals = file_to_dict(file_io)
        LOGGER.debug(vals)
        self.assertEqual(6, len(vals))
        for tran in vals:
            LOGGER.debug(tran)
            if tran['account_title'] == 'ACCOUNT TITLE1------------------':
                self.assertEqual(tran['amount'], '0000000123')
                self.assertEqual(tran['bsb_number'], '484-799')
                self.assertEqual(tran['account_number'], '123456789')
            elif tran['account_title'] in (
                    'ACCOUNT TITLE2------------------',
                    'ACCOUNT TITLE3------------------',
                    'ACCOUNT TITLE4------------------',
                    'ACCOUNT TITLE5------------------',
                    'ACCOUNT TITLE6------------------'
            ):
                pass
            else:
                self.fail('unexpected account title [{}]'.format(tran['account_title']))

    def test_file_to_dict_bad_record_type(self):
        file_content = (
            u"x                 01SUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"y484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"z999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                file_to_dict(file_io)
        self.assertEqual(exc.exception.args[0], 'Invalid record type - record_type=[x], last_record_type=[S]')

    def test_file_to_dict_bad_detail_record_data(self):
        file_content = (
            u"0                 01SUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"1x84-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                file_to_dict(file_io)
        self.assertEqual(exc.exception.args[0], 'Invalid record format - de detail')

    def test_file_to_dict_bad_header_record_data(self):
        file_content = (
            u"0                 0xSUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                file_to_dict(file_io)
        self.assertEqual(exc.exception.args[0], 'Invalid record format - de header')

    def test_file_to_dict_detail_without_header(self):
        # start of file
        file_content = (
            u"1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                file_to_dict(file_io)
        self.assertEqual('Invalid record type - record_type=[1], last_record_type=[S]', exc.exception.args[0])

        # middle of file
        file_content = (
            u"0                 01SUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
            u"1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                file_to_dict(file_io)
        self.assertEqual('Invalid record type - record_type=[1], last_record_type=[7]', exc.exception.args[0])

    def test_dict_to_file_multiple_headers(self):
        tran_template = {
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
            'withholding_tax_amount': '0000000000',
        }

        tran_db_1 = copy.deepcopy(tran_template)
        tran_db_1['tran_code'] = '13'
        tran_db_1['amount'] = '0000000123'

        tran_db_2 = copy.deepcopy(tran_template)
        tran_db_2['user_num'] = '654321'
        tran_db_2['tran_code'] = '13'
        tran_db_2['amount'] = '0000000123'

        tran_cr_1 = copy.deepcopy(tran_template)
        tran_cr_1['user_num'] = '654321'
        tran_cr_1['tran_code'] = '53'
        tran_cr_1['amount'] = '0000001122'

        tran_cr_2 = copy.deepcopy(tran_template)
        tran_cr_2['user_num'] = '654321'
        tran_cr_2['tran_code'] = '53'
        tran_cr_2['amount'] = '0000005566'

        stream = dict_to_file([tran_db_1, tran_cr_1, tran_cr_2, tran_cr_1, tran_db_1, tran_db_2])

        output = stream.readlines()

        # check that 10 lines outputted
        self.assertEqual(10, len(output))

        # check record type order is correct
        record_sequence = ''.join([line[0:1] for line in output])
        self.assertTrue(re.match(r'^(0([123])*7)*$', record_sequence))

    def test_convert_json_1_credit(self):
        # check that convert function works for json format
        expected_direct_entry_dict = {
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

        json_dict = {
            'to_routing': '484-799',
            'to_name': 'account title',
            'to_account': '123456789',
            'from_account': '123456789',
            'amount': 200,
            'from_name': 'MR DELOSA',
            'from_routing': '484-799',
            'tran_type': 'cr',
            'to_description': 'lodgement ref',
            'post_date': date(2016, 12, 1).isoformat()
            }

        direct_entry_dict = convert_json_1(json_dict)
        self.maxDiff = None
        self.assertEqual(expected_direct_entry_dict, direct_entry_dict)

    def test_convert_json_1_debit(self):
        # check that convert function works for json format
        expected_direct_entry_dict = {
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
            'tran_code': '13',
            'amount': '0000000200',  # $2.00
            'account_title': 'account title',
            'lodgement_ref': 'lodgement ref',
            'trace_bsb_number': '484-799',
            'trace_account_number': '123456789',
            'name_of_remitter': 'MR DELOSA',
            'withholding_tax_amount': '00000000',
        }

        json_dict = {
            'to_routing': '484-799',
            'to_name': 'account title',
            'to_account': '123456789',
            'from_account': '123456789',
            'amount': 200,
            'from_name': 'MR DELOSA',
            'from_routing': '484-799',
            'tran_type': 'db',
            'to_description': 'lodgement ref',
            'post_date': date(2016, 12, 1).isoformat()}

        direct_entry_dict = convert_json_1(json_dict)
        self.maxDiff = None
        self.assertEqual(expected_direct_entry_dict, direct_entry_dict)


if __name__ == '__main__':
    unittest.main()
