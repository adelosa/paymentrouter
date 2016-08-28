"""
# pr_file_collection

process incoming file based payments

## config json file format.

{
    "source: 'RBA',
    "format": {
        "name": "direct_entry",
        "version": 1
    },
    "routing": {
        "001_less_than_100" : {
            "rule_function" : "minimum_amount_routing",
            "rule_value" : 100,
            "queue" : "less_than_100"
            },
        "002_less_than_200" : {
            "rule_function" : "minimum_amount_routing",
            "rule_value" : 200,
            "queue" : "less_than_200"
            },
        "099_bsb_route" : {
            "rule_function" : "route_rule_direct_entry_bsb",
            "rule_value" : "^(57993[0-9]|484799)$",
            "queue" : "de_onus"
            }
    }
}

- add to dict processing_date from command line (odate)

"""
import json
import logging
from datetime import datetime

import click
from mongoengine import connect
from paymentrouter.MessageRouter import MessageRouter, get_format_module_function, get_format_module_name
from paymentrouter.model.Message import Message, build_message

LOGGER = logging.getLogger(__name__)


class CommandArgs:
    """
    command line parameter storage
    """
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


def convert_input(input_format, input_file_handle):
    """
    convert file to dict format based on format.name and format.version value
    dynamically load from library - message_type.{{ format.name }}_{{ format.version }}
    function signature - file_to_dict(filename) returns [{dict},{dict}..]

    :param input_format: dict with name, version keys
        { 'name': 'format_name', 'version': 1 }
    :param input_file_handle: file handle to input
    :return: dict containing file records
    """
    func = get_format_module_function(input_format, 'file_to_dict')
    return func(input_file_handle)


def route_items(input_dict, routing, input_format):
    """
    determine and add queue key to input_dict
    :param input_dict: list of dict entries
    :param routing: routing config in dict
    :param input_format: input_dict format as { name: x, version: 1 }
    :return: None
    """
    router = MessageRouter()
    router.output_routing_rules = routing
    for input_item in input_dict:
        queue = router.get_message_output_queue(
            input_item, default_rule_module=get_format_module_name(input_format))
        input_item['queue'] = queue


def write_to_mongo(input_records, db_host, db_name):
    """
    Write input_dict to mongo. Queue determines collection
    :param input_records: list of dict containing data
    :param db_host: mongo host name
    :param db_name: mongo db name
    :return: None
    """
    click.echo("Connecting to mongo at {} {}".format(db_host, db_name))
    connect(db_name, host=db_host)

    Message.objects.insert(input_records)


def create_records(input_dict, config):
    """
    formats mongoengine record from transaction
    :param input_dict: list of dicts containing data
    :param config: json job config
    :return: list of mongoengine documents
    """
    router = MessageRouter()
    router.output_routing_rules = config['routing']

    output_template = {
        'source': config['source'],
        'format': config['format']['name'],
        'version': config['format']['version']
    }

    output_records = []
    for input_record in input_dict:

        # determine queue to route to
        queue = router.get_message_output_queue(
            input_record,
            default_rule_module=get_format_module_name(config['format'])
        )
        # build message
        output_record = build_message(
            data=input_record,
            queue=queue,
            template=output_template,
            payment_date=datetime.today().date()
        )
        output_records.append(output_record)

    return output_records


@pass_args
def run(args):
    """
    run file collection
    :param args: input args
    :return: None
    """
    # load window config
    config = load_json_config(args.config_file)

    # load input file and convert to dict
    file_dict = convert_input(config['format'], args.input_file)
    LOGGER.debug("BEFORE: file_dict=%s", file_dict)

    # create transaction documents
    records = create_records(file_dict, config)

    # write the trans to mongo using queue = collection
    write_to_mongo(records, args.db_host, args.db_name)


@click.command()
@click.argument('config-file', type=click.File('r'))
@click.argument('input-file', type=click.File('r'))
@click.option('--db-host', envvar='PR_DB_HOST', default='127.0.0.1')
@click.option('--db-name', envvar='PR_DB_NAME', default='paymentrouter')
@pass_args
def pr_file_collection(args, config_file, input_file, db_host, db_name):
    """
    run file collection cli
    :param args:
    :param config_file:
    :param input_file:
    :param db_host:
    :param db_name:
    :return:
    """
    args.config_file = config_file
    args.input_file = input_file
    args.db_host = db_host
    args.db_name = db_name
    run()
