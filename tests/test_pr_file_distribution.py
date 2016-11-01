"""
test cases for pr_file_distribution
"""
from __future__ import absolute_import

import unittest
import logging
import os
from datetime import date, datetime
import time

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

    def test_json_end_to_end(self):
        self.end_to_end_run('json')
        self.end_to_end_run('direct_entry')

    def end_to_end_run(self, format_name):
        config = """
{
    "format": {
        "name": "{{format_name}}",
        "version": 1
    },
    "queue": "on-us"
}
        """
        config = config.replace('{{format_name}}', format_name)

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
            'user_name': 'DE USER NAME',
            'user_num': '654321',
            'file_desc': 'DE FILE DESC',
            'date_for_process': '011216',
            'bsb_number': '484-799',
            'account_number': '111111111',
            'indicator': ' ',
            'tran_code': '53',
            'amount': '0000012345',  # $2.00
            'account_title': 'DE ACCT TITLE',
            'lodgement_ref': 'DE LODGE REF',
            'trace_bsb_number': '484-799',
            'trace_account_number': '222222222',
            'name_of_remitter': 'DE REMITTER NAME',
            'withholding_tax_amount': '00000000',
        }

        # json payment data
        json_data = {
            'from_account': '987654321',
            'from_routing': '484-799',
            'to_description': 'JSON TO DESC',
            'from_name': 'JSON FROM NAME',
            'tran_type': 'cr',
            'to_name': 'JSON TO NAME',
            'to_account': '333333333',
            'to_routing': '484-799',
            'amount': 54321,
            'post_date': date(2016, 12, 2)
        }

        tran_list = []
        for tran_id in range(0, 100, 2):
            tran_list.append(
                build_message(
                    submission_id=str(tran_id),
                    collection_data=de_data,
                    template=message_template,
                    queue='on-us'
                )
            )
            tran_list.append(
                build_message(
                    submission_id=str(tran_id+1),
                    collection_data=json_data,
                    collection_format_name='json',
                    template=message_template,
                    queue='on-us'
                )
            )

        with testing.postgresql.Postgresql() as postgresql:
            # setup test database
            LOGGER.debug('Creating postgresql instance for testing')
            LOGGER.debug('  url={}'.format(postgresql.url()))
            LOGGER.debug('  data directory={}'.format(postgresql.get_data_directory()))

            engine = create_engine(postgresql.url(), json_serializer=dumps)
            alembic_cfg = Config("alembic.ini")

            with engine.begin() as connection:
                alembic_cfg.attributes['connection'] = connection
                command.upgrade(alembic_cfg, "head")

            Session = sessionmaker(bind=engine)
            session = Session()
            session.add_all(tran_list)
            session.commit()
            session.close()

            # run the job
            runner = CliRunner()
            with runner.isolated_filesystem() as fs:
                with open('test.json', 'w') as fp:
                    fp.write(config)
                start_time = time.clock()
                result = runner.invoke(
                    pr_file_distribution,
                    ['test.json', 'out-json.txt', '--db-url', postgresql.url()],
                    catch_exceptions=False
                )
                duration = time.clock() - start_time
                divider = '.'*20
                LOGGER.debug('output:\n%s', result.output)
                LOGGER.debug('exception:\n%s', result.exception)
                outfile = os.path.join(fs, 'out-json.txt')
                print(divider)
                with open(outfile, 'r') as out_fh:
                    record_count = 0
                    for line in out_fh:
                        print(line.rstrip())
                        record_count += 1
                    print("Processed {} lines".format(record_count))
                print("{}\nRun completed in {} seconds\n{}".format(divider, duration, divider))
