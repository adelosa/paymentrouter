"""
pr_file_distribution

For a given destination queue, get all payments and extract in format

## config json file format.

{
    "format": {
        "name": "direct_entry",
        "version": 1
    },
    "queue": "de_onus"
}

"""
import json
import logging
import datetime

import click
from mongoengine import connect, Q

from paymentrouter.model.Message import Message

LOGGER = logging.getLogger(__name__)


class CommandArgs:
    def __init__(self):
        pass

pass_args = click.make_pass_decorator(CommandArgs, ensure=True)


def load_json_config(config_file_handle):
    """
    load window config
    :param config_file_handle: file handle for window config file
    :return: dict config
    """
    return json.load(config_file_handle)


@pass_args
def run(args):

    # load distribution config
    config = load_json_config(args.config_file)
    format_info = config['format']

    # get all undistributed trans for queue that are not in the output format from config
    connect(args.db_name, host=args.db_host)
    messages = Message.objects(
        Q(distribution__queue=config['queue']) &
        Q(status='ready') &
        Q(payment_date__lte=datetime.datetime.today()) & (
            Q(collection__format__name__ne=format_info['name']) |
            Q(collection__format__version__ne=format_info['version'])
        )
    )
    # for each transaction, convert tran to output format - same record
    LOGGER.debug("NumberOfEntries:%s", len(messages))

    # get all undistributed trans for queue

    # call dict_to_file for output format provided in config

    # update all records to mark as processed


@click.command()
@click.argument('config-file', type=click.File('r'))
@click.option('--db-host', envvar='PR_DB_HOST', default='127.0.0.1')
@click.option('--db-name', envvar='PR_DB_NAME', default='paymentrouter')
@pass_args
def pr_file_distribution(args, config_file, db_host, db_name):
    args.config_file = config_file
    args.db_host = db_host
    args.db_name = db_name
    run()
