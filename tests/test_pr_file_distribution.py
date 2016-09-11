"""
test cases for pr_file_distribution
"""
from __future__ import absolute_import
import unittest
import logging
from datetime import date

from click.testing import CliRunner
from mongoengine import connect

from paymentrouter.cli.pr_file_distribution import pr_file_distribution
from paymentrouter.model.Message import Message, build_message


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


class PRFileDistributionTestCase(unittest.TestCase):

    def test_cli_run_help(self):
        runner = CliRunner()
        result = runner.invoke(pr_file_distribution, ['--help'])
        LOGGER.debug(result.output)
        self.assertTrue(True)

    def test_cli_run(self):
        config = """
{
    "format": {
        "name": "json",
        "version": 1
    },
    "queue": "on-us"
}
        """

        # add some data to mongo
        message_template = {
            'source': 'RBA',
            'format_name': 'direct_entry',
            'format_version': 1,
            'queue': 'on-us',
            'status': 'ready',
            'payment_date': date(2000, 1, 1),
            'data': {
                'key': 'the value'
            }
        }

        connect('test', host='mongomock://localhost')
        Message.drop_collection()

        de_data = {
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

        message = build_message(data=de_data, template=message_template)
        message.save()
        json_data = {
            'from_account': '123456789',
            'from_routing': '484-799',
            'to_description': 'lodgement ref',
            'from_name': 'MR DELOSA',
            'tran_type': 'cr',
            'to_name': 'account title',
            'to_account': '123456789',
            'to_routing': '484-799',
            'amount': 200,
            'post_date': date(2016, 12, 2)
        }
        message = build_message(data=json_data, format_name='json', template=message_template)
        message.save()

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.json', 'w') as fp:
                fp.write(config)
            result = runner.invoke(pr_file_distribution, ['test.json', '--db-name', 'test', '--db-host', "mongomock://localhost"], catch_exceptions=True)
        LOGGER.debug("output:\n%s", result.output)
        LOGGER.debug("exception:\n%s", result.exception)
        self.assertEqual(0, result.exit_code)

        for message in Message.objects():
            print(repr(message))
            print(message.collection.format.name)
            print(message.collection.format.version)
            print(message.collection.data)
            if message.distribution is not None:
                # print(message.distribution.format.name)
                # print(message.distribution.format.version)
                print(message.distribution.data)
            else:
                print("no distribution data found!")
