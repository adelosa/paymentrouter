"""
test cases for pr_file_distribution
"""
from __future__ import absolute_import

import unittest
import logging
import os
from datetime import date, datetime

from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
import testing.postgresql

from paymentrouter.model import dumps
from paymentrouter.model.Transaction import TransactionStatus, build_message
from paymentrouter.cli.pr_file_distribution import pr_file_distribution

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

        # transaction template
        message_template = {
            'source': 'RBA',
            'status': TransactionStatus.ready,
            'collection_format_name': 'direct_entry',
            'collection_format_version': 1,
            'collection_data': {},
            'collection_datetime': datetime.today().date(),
            'queue': 'default',
        }

        # direct entry data
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

        # json payment data
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

        de_tran = build_message(
            submission_id='1',
            collection_data=de_data,
            template=message_template,
            queue='on-us'
        )

        json_tran = build_message(
            submission_id='2',
            collection_data=json_data,
            collection_format_name='json',
            template=message_template,
            queue='on-us'
        )

        with testing.postgresql.Postgresql() as postgresql:
            # setup test database
            print('Creating postgresql instance for testing')
            print('  url={}'.format(postgresql.url()))
            print('  data directory={}'.format(postgresql.get_data_directory()))

            engine = create_engine(postgresql.url(), echo=True, json_serializer=dumps)
            alembic_cfg = Config("alembic.ini")

            with engine.begin() as connection:
                alembic_cfg.attributes['connection'] = connection
                command.upgrade(alembic_cfg, "head")

            Session = sessionmaker(bind=engine)
            session = Session()
            session.add(de_tran)
            session.add(json_tran)
            session.commit()
            session.close()

            # run the job
            runner = CliRunner()
            with runner.isolated_filesystem() as fs:
                with open('test.json', 'w') as fp:
                    fp.write(config)
                result = runner.invoke(pr_file_distribution, ['test.json', '--db-url', postgresql.url()], catch_exceptions=False)
                LOGGER.info("output:\n%s", result.output)
                LOGGER.info("exception:\n%s", result.exception)

                print(fs)
                # wp = Path(fs)
                outfile = os.path.join(fs, 'out-json.txt')
                print('.' * 20)
                with open(outfile, 'r') as outfh:
                    outdata = outfh.read()
                print(outdata)
                print('.' * 20)

            self.assertEqual(0, result.exit_code)
