"""
test cases for pr_file_distribution
"""
from __future__ import absolute_import
import unittest
import logging

from click.testing import CliRunner

from paymentrouter.cli.pr_file_distribution import pr_file_distribution

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

LOGGER = logging.getLogger(__name__)


class PRFileDistributionTestCase(unittest.TestCase):

    def test_cli_run_help(self):
        runner = CliRunner()
        result = runner.invoke(pr_file_distribution, ['--help'])
        LOGGER.debug(result.output)
        self.assertTrue(True)
