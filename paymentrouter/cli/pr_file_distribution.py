"""
pr_file_distribution

For a given destination queue, get all unprocessed payments and extract in format

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
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from paymentrouter.MessageRouter import get_format_module_function
from paymentrouter.model import dumps
from paymentrouter.model.SystemControl import SystemControl
from paymentrouter.model.Transaction import Transaction, TransactionStatus

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


def bridge_data(collection_format, distribution_format, collection_data):
    """
    converts data from collection to distribution format.
    logic for this will reside in distribution message type module
    :param collection_format:
    :param distribution_format:
    :param collection_data:
    :return:
    """
    func = get_format_module_function(
        distribution_format, 'convert_{0}_{1}'.format(collection_format['name'], collection_format['version'])
    )
    return func(collection_data)


def create_file(distribution_format, distribution_data):
    """
    converts data from collection to distribution format.
    logic for this will reside in distribution message type module
    :param distribution_format:
    :param distribution_data:
    :return:
    """
    func = get_format_module_function(distribution_format, 'dict_to_file')
    return func(distribution_data)


@pass_args
def run(args):

    # load distribution config
    config = load_json_config(args.config_file)
    format_info = config['format']

    engine = create_engine(args.db_url, json_serializer=dumps)
    Session = sessionmaker(bind=engine)
    session = Session()

    # get the system effective data
    effective_date = session.query(SystemControl.effective_date).one()

    # get all transactions ready to be processed for this queue
    messages = session.query(Transaction).filter(
        Transaction.queue == config['queue'],
        Transaction.status == TransactionStatus.ready,
        or_(Transaction.distribution_date <= effective_date,
            Transaction.distribution_date.is_(None)),
    ).all()

    # set the distribution data
    for message in messages:
        if (
            message.collection_format_name != format_info['name'] or
            message.collection_format_version != format_info['version']
        ):
            # bridge to new format if required
            LOGGER.debug('format [{}]:[{}] != [{}]:[{}]'.format(
                message.collection_format_name,
                message.collection_format_version,
                format_info['name'],
                format_info['version'])
            )
            coll_format = {'name': message.collection_format_name, 'version': message.collection_format_version}
            message.distribution_data = bridge_data(coll_format, format_info, message.collection_data)
        else:
            # just move the data across
            message.distribution_data = message.collection_data
        # add message.distribution.format info
        message.distribution_format_name = format_info['name']
        message.distribution_format_version = format_info['version']

    # get all the distribution data records into a list
    distribution_list = [message.distribution_data for message in messages]

    # call dict_to_file for output format provided in config
    output_stream = create_file(format_info, distribution_list)

    # write to output file
    args.output_file.write(output_stream.read())

    # update all records to mark as processed
    for message in messages:
        message.status = TransactionStatus.processed
        message.distribution_date = datetime.datetime.today().date()

    # write to the database
    session.commit()


@click.command()
@click.argument('config-file', type=click.File('r'))
@click.argument('output-file', type=click.File('w'))
@click.option('--db-url', envvar='PR_DB_URL', default='postgresql://postgres@127.0.0.1/test')
@pass_args
def pr_file_distribution(args, config_file, output_file, db_url):
    args.config_file = config_file
    args.output_file = output_file
    args.db_url = db_url
    run()
