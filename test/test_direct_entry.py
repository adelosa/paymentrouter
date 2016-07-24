from __future__ import absolute_import
import unittest
import logging

from io import StringIO

from paymentrouter.message_type.direct_entry_1 import file_to_dict

LOGGER = logging.getLogger(__name__)


class MessageTypeDirectEntryTestCase(unittest.TestCase):
    def test_file_to_dict(self):
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
            if tran['data']['account_title'] == 'ACCOUNT TITLE1------------------':
                self.assertEqual(tran['data']['amount'], '0000000123')
                self.assertEqual(tran['data']['bsb_number'], '484-799')
                self.assertEqual(tran['data']['account_number'], '123456789')
            elif tran['data']['account_title'] in (
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
                val = file_to_dict(file_io)
        print(exc.msg)

    def test_file_to_dict_bad_detail_record_data(self):
        file_content = (
            u"0                 01SUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"1x84-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                val = file_to_dict(file_io)
        self.assertEqual(exc.exception.args[0], 'Invalid record format - de detail')

    def test_file_to_dict_bad_header_record_data(self):
        file_content = (
            u"0                 0xSUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            u"1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            u"7999-999            000000000100000000010000000001                        000001                                        \n"
        )
        with self.assertRaises(Exception) as exc:
            with StringIO(file_content) as file_io:
                val = file_to_dict(file_io)
        self.assertEqual(exc.exception.args[0], 'Invalid record format - de header')


if __name__ == '__main__':
    unittest.main()
