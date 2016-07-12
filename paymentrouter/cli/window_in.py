"""
# window_in

process incoming file based payments

## window_in config
json file format.

{
    "filename": "/my/file/location",
    "format": {
        "name": "direct_entry",
        "version": 1
    }
    "routing": {
        "001_less_than_100" : {
            "rule_module" : "dummy",
            "rule_function" : "minimum_amount_routing",
            "rule_value" : 100,
            "queue" : "less_than_100"
            },
        "002_less_than_200" : {
            "rule_module" : "dummy",
            "rule_function" : "minimum_amount_routing",
            "rule_value" : 200,
            "queue" : "less_than_200"
            },
        "099_bsb_route" : {
            "rule_module" : "paymentrouter.message_type.direct_entry",
            "rule_function" : "route_rule_direct_entry_bsb",
            "rule_value" : "^(57993[0-9]|484799)$",
            "queue" : "de_onus"
            }
    }
}


- read json config
- check for presence of filename
- **TODO** if not present, wait x seconds.. count 10, then exit
- load filename into memory
- add to dict format.name as format_name
- add to dict format.version as format_version
- add to dict processing_date from command line (odate)

for each item in file [{dict}]
    - load routing rules
    - run through message_router
    - add message_router output to dict as output_queue

for each output_queue
    - write records to mongo - collection=queue
"""
import json
import click

from paymentrouter.MessageRouter import MessageRouter


class CommandArgs:
    def __init__(self):
        pass

pass_args = click.make_pass_decorator(CommandArgs, ensure=True)


def load_json_config(config_file):
    return json.load(config_file)


def convert_input(input_format, input_file_handle):
    """
    convert file to dict format based on format.name and format.version value
    dynamically load from library - message_type.{{ format.name }}_{{ format.version }}
    function signature - file_to_dict(filename) returns [{dict},{dict}..]

    :param input_format: dict containing name and version of format
        { 'name': 'format_name', 'version': 1 }
    :param input_file: file handle to input
    :return: dict containing file records
    """
    mod_name = '.'.join(
        ['paymentrouter', 'message_type', input_format['name']+'_'+str(input_format['version'])]
    )
    mod = __import__(mod_name, fromlist=['file_to_dict'])
    func = getattr(mod, 'file_to_dict')
    return func(input_file_handle)


def route_items(file_dict, routing):
    router = MessageRouter()
    router.output_routing_rules = routing
    for file_item in file_dict:
        queue = router.get_message_output_queue(file_item)
        file_item['queue'] = queue


def write_to_mongo(file_dict):
    print(file_dict)


@pass_args
def run(args):
    # load window config
    config = load_json_config(args.config_file)
    # load input file and convert
    with open(config['input_file']) as input_file_handle:
        file_dict = convert_input(config['format'], input_file_handle)
    # determine item routing
    route_items(file_dict, config['routing'])
    # write the trans to mongo using queue = collection
    write_to_mongo(file_dict)


@click.command()
@click.argument('config-file', type=click.File('r'))
@pass_args
def cli_entry(args, config_file):
    """
    Run an input window
    """
    args.config_file = config_file
    run()
