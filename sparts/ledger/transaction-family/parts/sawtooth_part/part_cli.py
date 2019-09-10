# Copyright 2017 Intel Corporation
# Copyright 2017 Wind River

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from __future__ import print_function

import argparse
import configparser
import getpass
import logging
import os
import traceback
import sys
import shutil
import pkg_resources
import json
import re

from colorlog import ColoredFormatter

import sawtooth_signing.secp256k1_signer as signing

from sawtooth_part.part_batch import PartBatch
from sawtooth_part.exceptions import PartException


DISTRIBUTION_NAME = 'sawtooth-part'


def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog


def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))


def add_create_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('create', parents=[parent_parser])

    parser.add_argument(
        'pt_id',
        type=str,
        help='an identifier for the part')
    
    parser.add_argument(
        'pt_name',
        type=str,
        help='provide part name')
    
    parser.add_argument(
        'checksum',
        type=str,
        help='Provide checksum')
    
    parser.add_argument(
        'version',
        type=str,
        help='provide version for the part')
    
    parser.add_argument(
        'src_uri',
        type=str,
        help='provide Source URI')
    
    parser.add_argument(
        'licensing',
        type=str,
        help='provide licensing')
    
    parser.add_argument(
        'label',
        type=str,
        help='provide label')
    
    parser.add_argument(
        'description',
        type=str,
        help='provide description')


    parser.add_argument(
        '--disable-client-validation',
        action='store_true',
        default=False,
        help='disable client validation')


def add_init_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('init', parents=[parent_parser])

    parser.add_argument(
        '--username',
        type=str,
        help='the name of the user')

    parser.add_argument(
        '--url',
        type=str,
        help='the url of the REST API')



def add_list_part_parser(subparsers, parent_parser):
    subparsers.add_parser('list-part', parents=[parent_parser])


def add_retrieve_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('retrieve', parents=[parent_parser])

    parser.add_argument(
        'pt_id',
        type=str,
        help='part identifier')


def add_envelope_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('AddEnvelope', parents=[parent_parser])
    
    parser.add_argument(
        'pt_id',
        type=str,
        help='part identifier')

    parser.add_argument(
        'envelope_id',
        type=str,
        help='the UUID identifier for envelope')


def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='enable more verbose output')

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='print version information')

    parent_parser.add_argument(
        '--auth-user',
        type=str,
        help='username for authentication if REST API is using Basic Auth')

    parent_parser.add_argument(
        '--auth-password',
        type=str,
        help='password for authentication if REST API is using Basic Auth')

    return parent_parser


def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    add_create_parser(subparsers, parent_parser)
    add_init_parser(subparsers, parent_parser)
    add_list_part_parser(subparsers, parent_parser)
    add_retrieve_parser(subparsers, parent_parser)
    add_envelope_parser(subparsers, parent_parser)
    add_supplier_parser(subparsers,parent_parser)
    add_category_parser(subparsers,parent_parser)

    return parser


def add_category_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('AddCategory', parents=[parent_parser])
    
    parser.add_argument(
        'pt_id',
        type=str,
        help='the identifier for the part')

    parser.add_argument(
        'category_id',
        type=str,
        help='the identifier for Supplier')

# Provide the UUID of the parent artifact and the UUID of the supplier
def add_supplier_parser(subparsers, parent_parser):
    parser = subparsers.add_parser('AddSupplier', parents=[parent_parser])
    
    parser.add_argument(
        'pt_id',
        type=str,
        help='the identifier for the part')

    parser.add_argument(
        'supplier_id',
        type=str,
        help='the identifier for Supplier')
    

def do_init(args, config):
    username = config.get('DEFAULT', 'username')
    if args.username is not None:
        username = args.username

    url = config.get('DEFAULT', 'url')
    if args.url is not None:
        url = args.url

    config.set('DEFAULT', 'username', username)
    print("set username: {}".format(username))
    config.set('DEFAULT', 'url', url)
    print("set url: {}".format(url))

    save_config(config)

    priv_filename = config.get('DEFAULT', 'key_file')
    if priv_filename.endswith(".priv"):
        addr_filename = priv_filename[0:-len(".priv")] + ".addr"
    else:
        addr_filename = priv_filename + ".addr"

    if not os.path.exists(priv_filename):
        try:
            if not os.path.exists(os.path.dirname(priv_filename)):
                os.makedirs(os.path.dirname(priv_filename))

            privkey = signing.generate_privkey()
            pubkey = signing.generate_pubkey(privkey)
            addr = signing.generate_identifier(pubkey)

            with open(priv_filename, "w") as priv_fd:
                print("writing file: {}".format(priv_filename))
                priv_fd.write(privkey)
                priv_fd.write("\n")

            with open(addr_filename, "w") as addr_fd:
                print("writing file: {}".format(addr_filename))
                addr_fd.write(addr)
                addr_fd.write("\n")
        except IOError as ioe:
            raise PartException("IOError: {}".format(str(ioe)))




def do_list_part(args, config):
    url = config.get('DEFAULT', 'url')
    key_file = config.get('DEFAULT', 'key_file')
    auth_user, auth_password = _get_auth_info(args)

    client = PartBatch(base_url=url, keyfile=key_file)

    result = client.list_part(auth_user=auth_user,
                                 auth_password=auth_password)

    if result is not None:
        output = refine_output(str(result))
        print(output)
    else:
        raise PartException("Could not retrieve part listing.")


def do_retrieve(args, config):
    
    pt_id = args.pt_id

    url = config.get('DEFAULT', 'url')
    key_file = config.get('DEFAULT', 'key_file')
    auth_user, auth_password = _get_auth_info(args)

    client = PartBatch(base_url=url, keyfile=key_file)

    result = client.retrieve_part(pt_id, auth_user=auth_user, auth_password=auth_password).decode()

    if result is not None:
        result = filter_output(str(result))
        print(result)
     
    else:
        raise PartException("Part not found: {}".format(pt_id))



def filter_output(inputstr):
    
    ptlist = inputstr.split(',',1)
    ptstr = ptlist[1]
    jsonstr = ptstr.replace('pt_id','uuid').replace('pt_name','name')
    data = json.loads(jsonstr)
    data = removekey(data,'categories')
    data = removekey(data,'envelopes')
    data = removekey(data,'suppliers')
    jsonstr = json.dumps(data)
    return jsonstr


def amend_supplier_fields(inputstr):
    output = inputstr.replace("\\","").replace('supplier_id','uuid').replace('supplier_name','name').replace('supplier_url','url')
    return output

        
def refine_output(inputstr):
    outputstr = ''
    catstr = "\"categories\": "
    supplierstr = "\"suppliers\": "
    envelopestr = "\"envelopes\": "
    inputstr = inputstr[1:-1]
    instr = re.sub(r'\[.*?\]', '',inputstr)
    outputstr= instr.replace(catstr+",","").replace(", "+catstr,"").replace('b\'','').replace('}\'','}').replace(supplierstr+",","").replace(", "+supplierstr,"")
    outputstr = outputstr[:-1]
    slist = outputstr.split("},")
    supplierlist = []
    for line in slist:
        record = "{"+line.split(",{",1)[-1]+"}"
        supplierlist.append(record)
    joutput = str(supplierlist)
    joutput = joutput.replace(envelopestr+",","").replace(", "+envelopestr,"")
    joutput = joutput.replace("'{","{").replace("}'","}").replace(", { {",", {")
    joutput = amend_supplier_fields(joutput)
    return joutput

def do_create(args, config):
 
    pt_id = args.pt_id
    pt_name = args.pt_name
    checksum = args.checksum
    version = args.version
    src_uri = args.src_uri
    licensing = args.licensing
    label = args.label
    description = args.description

    url = config.get('DEFAULT', 'url')
    key_file = config.get('DEFAULT', 'key_file')
    auth_user, auth_password = _get_auth_info(args)

    client = PartBatch(base_url=url, keyfile=key_file)

   
    response = client.create(
            pt_id,pt_name,checksum,version,src_uri,licensing,label,description,
            auth_user=auth_user,
            auth_password=auth_password)
    print_msg(response)



def add_Category(args, config):
    pt_id = args.pt_id
    category_id = args.category_id
   
    url = config.get('DEFAULT', 'url')
    key_file = config.get('DEFAULT', 'key_file')

    client = PartBatch(base_url=url,
                      keyfile=key_file)
    response = client.add_category(pt_id,category_id)
    
    print_msg(response)


def do_add_envelope(args, config):
    pt_id = args.pt_id
    envelope_id = args.envelope_id
   
    url = config.get('DEFAULT', 'url')
    key_file = config.get('DEFAULT', 'key_file')

    client = PartBatch(base_url=url,
                      keyfile=key_file)
    response = client.add_envelope(pt_id,envelope_id)
    
    print_msg(response)


def print_msg(response):
    if "batch_status?id" in response:
        print ("{\"status\":\"success\"}")
    else:
        print ("{\"status\":\"exception\"}")

# add the relationship between parent artifact and supplier
def add_Supplier(args, config):
    pt_id = args.pt_id
    supplier_id = args.supplier_id
   
    url = config.get('DEFAULT', 'url')
    key_file = config.get('DEFAULT', 'key_file')

    client = PartBatch(base_url=url,
                      keyfile=key_file)
    response = client.add_supplier(pt_id,supplier_id)
    
    print_msg(response)

def load_config():
    home = os.path.expanduser("~")
    real_user = getpass.getuser()

    config_file = os.path.join(home, ".sawtooth", "part.cfg")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    config = configparser.ConfigParser()
    config.set('DEFAULT', 'url', 'http://127.0.0.1:8080')
    config.set('DEFAULT', 'key_dir', key_dir)
    config.set('DEFAULT', 'key_file', '%(key_dir)s/%(username)s.priv')
    config.set('DEFAULT', 'username', real_user)
    if os.path.exists(config_file):
        config.read(config_file)

    return config


def save_config(config):
    home = os.path.expanduser("~")

    config_file = os.path.join(home, ".sawtooth", "part.cfg")
    if not os.path.exists(os.path.dirname(config_file)):
        os.makedirs(os.path.dirname(config_file))

    with open("{}.new".format(config_file), "w") as fd:
        config.write(fd)
    if os.name == 'nt':
        if os.path.exists(config_file):
            os.remove(config_file)
    os.rename("{}.new".format(config_file), config_file)


def _get_auth_info(args):
    auth_user = args.auth_user
    auth_password = args.auth_password
    if auth_user is not None and auth_password is None:
        auth_password = getpass.getpass(prompt="Auth Password: ")

    return auth_user, auth_password


def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    config = load_config()

    if args.command == 'create':
        do_create(args, config)
    elif args.command == 'init':
        do_init(args, config)
  
    elif args.command == 'list-part':
        do_list_part(args, config)
    elif args.command == 'retrieve':
        do_retrieve(args, config)
    elif args.command == 'AddEnvelope':
        do_add_envelope(args, config)     
    elif args.command == 'AddSupplier':
        add_Supplier(args, config)     
    elif args.command == 'AddCategory':
        add_Category(args, config)          
    else:
        raise PartException("invalid command: {}".format(args.command))

def removekey(d,key):
    r = dict(d)
    del r[key]
    return r

def main_wrapper():
    try:
        main()
    except PartException as err:
        errmsg = str(err)
        if '404' in errmsg:
            print("{\"status\":\"404 Not Found\"}")
        else:
            msg = "{\"error\":\"failed\",\"error_message\":\""
            closing_str = "\"}"
            print (msg+errmsg+closing_str)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
