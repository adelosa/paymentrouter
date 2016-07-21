"""
# pr_file_collection

process incoming file based payments

## config json file format.

{
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

import click
import pymongo

from paymentrouter.MessageRouter import MessageRouter

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


def get_format_module_name(input_format):
    """
    determine the module name from the input_format
    :param input_format: dict with name, version keys
    :return:
    """
    return '.'.join(
        ['paymentrouter', 'message_type', input_format['type']+'_'+str(input_format['version'])]
    )


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
    mod_name = get_format_module_name(input_format)
    mod = __import__(mod_name, fromlist=['file_to_dict'])
    func = getattr(mod, 'file_to_dict')
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


def write_to_mongo(input_dict, db_host, db_name):
    """
    Write input_dict to mongo. Queue determines collection
    :param input_dict: list of dict containing data
    :param db_host: mongo host name
    :param db_name: mongo db name
    :return: None
    """
    click.echo("Connecting to mongo at {} {}".format(db_host, db_name))
    client = pymongo.MongoClient("mongodb://" + db_host)
    db_client = client[db_name]

    # get the queues allocated in the input_dict
    queues = set([item['queue'] for item in input_dict])

    # write contents of each queue to collection
    for queue in queues:
        queue_dict_gen = filter(lambda d: d['queue'] == queue, input_dict)
        db_client[queue].insert_many(list(queue_dict_gen))


@pass_args
def run(args):
    """
    run a window
    :param args: input args
    :return: None
    """
    # load window config
    config = load_json_config(args.config_file)

    # load input file and convert
    file_dict = convert_input(config['format'], args.input_file)
    LOGGER.debug("BEFORE: file_dict=%s", file_dict)

    # determine item routing
    route_items(file_dict, config['routing'], config['format'])
    LOGGER.debug("ROUTE : file_dict=%s", file_dict)

    # write the trans to mongo using queue = collection
    write_to_mongo(file_dict, args.db_host, args.db_name)


@click.command()
@click.argument('config-file', type=click.File('r'))
@click.argument('input-file', type=click.File('r'))
@click.option('--db-host', envvar='WINDOW_DB_HOST', default='127.0.0.1')
@click.option('--db-name', envvar='WINDOW_DB_NAME', default='window')
@pass_args
def pr_file_collection(args, config_file, input_file, db_host, db_name):
    args.config_file = config_file
    args.input_file = input_file
    args.db_host = db_host
    args.db_name = db_name
    run()
