from __future__ import absolute_import
import sys
import unittest
import mock
import logging

from click.testing import CliRunner

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import testing.postgresql

from paymentrouter.cli.pr_file_collection import (
    convert_input, route_items, pr_file_collection, create_records
)
from paymentrouter.model.Transaction import Base, Transaction, TransactionStatus

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


def file_to_dict(file_handle):
    file_contents = file_handle.read()
    return {'id': 1, 'value': file_contents}


def dummy_rule(message, value):
    if message['value'] == value:
        return True
    return False


class PRFileCollectionTestCase(unittest.TestCase):

    @mock.patch('paymentrouter.message_type.direct_entry_1.file_to_dict', side_effect=file_to_dict)
    def test_convert_input(self, mock_message_type):
        builtin = 'builtins' if sys.version_info[0] == 3 else '__builtin__'
        with mock.patch('{}.open'.format(builtin), mock.mock_open(read_data='test')):
            with open('/dev/null') as file_handle:
                output = convert_input({'name': 'direct_entry', 'version': 1}, file_handle)
        self.assertEqual(output, {'id': 1, 'value': 'test'})

    @mock.patch(
        'paymentrouter.message_type.direct_entry_1.route_rule_direct_entry_bsb',
        side_effect=dummy_rule)
    def test_route_items(self, mock_rule):
        file_dict = [
            {'id': 1, 'value': 1},
            {'id': 2, 'value': 2},
            {'id': 3, 'value': 1},
        ]
        routing = {
            "rule1": {
                "rule_function": "route_rule_direct_entry_bsb",
                "rule_value": 1,
                "queue": "queue_1"
            },
        }
        file_format = {'name': 'direct_entry', 'version': 1}
        route_items(file_dict, routing, file_format)
        self.assertEqual(len(file_dict), 3)
        for item in file_dict:
            self.assertIn('id', item)
            self.assertIn('queue', item)
            if item['id'] in (1, 3):
                self.assertEqual(item['queue'], 'queue_1')
            else:
                self.assertEqual(item['queue'], 'default')

    @mock.patch(
        'paymentrouter.message_type.direct_entry_1.route_rule_direct_entry_bsb',
        side_effect=dummy_rule)
    def test_create_records(self, dummy_rule):
        config = {
            "source": 'ABC',
            "format": {'name': 'direct_entry', 'version': 1},
            "routing": {
                "rule1": {
                    "rule_function": "route_rule_direct_entry_bsb",
                    "rule_value": 1,
                    "queue": "queue_1"
                },
            },
        }
        output = create_records([{'value': 1}, {'value': 0}], config)
        self.assertEqual(2, len(output))
        self.assertEqual('queue_1', output[0].queue)
        self.assertEqual('default', output[1].queue)

    def test_cli_run_help(self):
        runner = CliRunner()
        result = runner.invoke(pr_file_collection, ['--help'])
        LOGGER.debug(result.output)
        self.assertTrue(True)

    def test_cli_run(self):
        """
        This is an end to end test which establishes a new postgresql db then runs a collection process
        with a sample config and input file
        :return:
        """
        config = """
{
    "source": "RBA",
    "format": {
        "name": "direct_entry",
        "version": 1
    },
    "routing": {
        "099_bsb_route" : {
            "rule_function" : "route_rule_direct_entry_bsb",
            "rule_value" : "^(579-93[0-9]|484-799)$",
            "queue" : "de_onus"
        }
    }
}
        """
        test_data = (
            "0                 01SUN       MR DELOSA PTY LTD---------123456PAYROLL PAYM011216                                        \n"
            "1484-799123456789 530000000123ACCOUNT TITLE1------------------LODGEMENT REFERENC484-799987654321MR DELOSA PTY LT00000000\n"
            "7999-999            000000000100000000010000000001                        000001                                        "
        )
        runner = CliRunner()

        with testing.postgresql.Postgresql() as postgresql:
            print('Creating postgresql instance for testing')
            print('  url={}'.format(postgresql.url()))
            print('  data directory={}'.format(postgresql.get_data_directory()))

            engine = create_engine(postgresql.url())
            Base.metadata.create_all(engine)

            with runner.isolated_filesystem():
                with open('test.json', 'w') as fp:
                    fp.write(config)
                with open('test.input.txt', 'w') as fp:
                    fp.write(test_data)
                result = runner.invoke(pr_file_collection, ['test.json', 'test.input.txt', '--db-url', postgresql.url()], catch_exceptions=True)

            # check the results from the database
            Session = sessionmaker(bind=engine)
            session = Session()

            transactions = session.query(Transaction).all()

            self.assertEqual(1, len(transactions), 'check that 1 record saved')
            LOGGER.debug(transactions[0])
            self.assertEqual('direct_entry', transactions[0].collection_format_name, 'check format name saved')
            self.assertEqual(1, transactions[0].collection_format_version, 'check format version saved')
            self.assertEqual('de_onus', transactions[0].queue, 'check correct queue saved')
            self.assertIsNone(transactions[0].distribution_data)
            self.assertIsNone(transactions[0].distribution_format_name)
            self.assertIsNone(transactions[0].distribution_format_version)
            self.assertIsNone(transactions[0].distribution_date)
            self.assertEqual(TransactionStatus.ready, transactions[0].status)

            session.commit()
            session.close()

        LOGGER.debug("proper_test:\n%s", result.output)
        LOGGER.debug(result.exception)
        self.assertEqual(0, result.exit_code)

if __name__ == '__main__':
    unittest.main()
