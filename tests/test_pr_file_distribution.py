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
        "name": "direct_entry",
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
            'payment_date': date(2000, 1, 1)
        }

        message = build_message(format_version=2, template=message_template)

        print(message.collection.source)

        connect('test', host='mongomock://localhost')
        message.save()

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.json', 'w') as fp:
                fp.write(config)
            result = runner.invoke(pr_file_distribution, ['test.json', '--db-host', "mongomock://localhost"], catch_exceptions=True)
        LOGGER.debug("output:\n%s", result.output)
        LOGGER.debug("exception:\n%s", result.exception)
        self.assertEqual(0, result.exit_code)
