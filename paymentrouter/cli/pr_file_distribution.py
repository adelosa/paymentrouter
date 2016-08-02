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
import logging
import click

LOGGER = logging.getLogger(__name__)


class CommandArgs:
    def __init__(self):
        pass

pass_args = click.make_pass_decorator(CommandArgs, ensure=True)


@click.argument('config-file', type=click.File('r'))
@click.option('--db-host', envvar='PR_DB_HOST', default='127.0.0.1')
@click.option('--db-name', envvar='PR_DB_NAME', default='window')
@pass_args
def pr_file_collection(args, config_file, db_host, db_name):
    args.config_file = config_file
    args.db_host = db_host
    args.db_name = db_name
    run()


def run():
    # get all undistributed trans for queue from mongo

    # call dict_to_file for format provided in config

    # update all records to mark as processed
    pass
