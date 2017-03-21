# -*- coding: utf-8 -*-

import os
import sys
import getpass
import yaml
import json
import argparse
import subprocess
import logging
from .utils import get_cli_version, find_executable_path, get_azurecli_modules_path, AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION

logger = logging.getLogger('index.generator')

_AZURE_SHELL_INDEX_GEN_USER = getpass.getuser()
_AZURE_SHELL_INDEX_GEN_USER_HOME = os.environ['HOME']

"""
Data Structure for Azure Shell Index
"""
def new_index_command_tree():
    return {'arguments': [],
            'argument_tree': {},
            'commands': [],
            'command_tree': {},
            'summary': ''
           }

"""
Data Structure for internal parsing Azure CLI Groups & Commands
groups_map
    group_name1 => group1 
                  -name
                  -summary
                  -subgroups = []
                  -commands =[]
   group_name2 => group2
    ...
commands_map
    cmd1        => cmd_object1
                  -summary
                  -arguments : []
                  -argument_tree : {}
                      arg1 => arg_object1 {}
                              -required
                              -options
                              -help
                      arg2 => arg_object2 
                      arg3 => arg_object3
                  -example
                  -command
                  -group
    cmd2        => cmd_object2
    ...
"""
def new_parsing_group():
    return {
        'name': '',
        'commands': [],
        'subgroups': [],
        'summary': '',
    }
def new_parsing_command():
    return {
        'summary': '',
        'arguments': [],
        'argument_tree': {},
        'example': '',
        'command': '',
        'group': ''
    }
def new_parsing_argument():
    return {
        'required': False,
        'options': '',
        'help': ''
    }

def dump_cmd_object(c):
    logger.debug("cmd dump: command:{} summary:{} arguments:{} example:{} group:{}".format(
            c['command'], c['summary'], "|".join(c['arguments']), c['example'], c['group']))

def dump_group_object(g):
    logger.debug("group dump:{} subgroup:{} summary:{} cmdlist={}".format(
            g['name'], "|".join(g['subgroups']), g['summary'], "|".join(g['commands'])))



def convert_help_column(c):
    c = c.replace(_AZURE_SHELL_INDEX_GEN_USER_HOME, '<HOME>')
    c = c.replace(_AZURE_SHELL_INDEX_GEN_USER, '<USER>')
    return c

IN_BLOCK_TYPE_NONE      = 0
IN_BLOCK_TYPE_COMMAND   = 1
IN_BLOCK_TYPE_ARGUMENTS = 2
IN_BLOCK_TYPE_EXAMPLES  = 3

def capture_cmd(cmd):
    logger.debug("Capturing command: {}".format(cmd))
    cmd_string = 'az {} -h'.format(cmd)
    proc = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    cmd_object= new_parsing_command()

    in_block_type = IN_BLOCK_TYPE_NONE
    cur_argument = ''
    while True:
        line = proc.stdout.readline()
        l = line.strip()
        if l =='Command':
            in_block_type = IN_BLOCK_TYPE_COMMAND
        elif l.find("Arguments") >= 0:
            in_block_type = IN_BLOCK_TYPE_ARGUMENTS
        elif l.find("Examples") >= 0:
            in_block_type = IN_BLOCK_TYPE_EXAMPLES
        elif l:
            if in_block_type == IN_BLOCK_TYPE_COMMAND:
                colon_pos = l.find(':')
                if colon_pos > 0:
                    l = l[colon_pos+1:].lstrip()
                cmd_object['summary'] = cmd_object['summary'] + l
            elif in_block_type ==IN_BLOCK_TYPE_ARGUMENTS:
                ### options
                if l[0:2] == '--':
                    arg_object = new_parsing_argument()
                    colon_pos = l.find(':')
                    options_column = l[0:colon_pos].rstrip()
                    help_column = l[colon_pos+1:].strip()
                    required_pos = options_column.find('[Required]')
                    options = options_column
                    is_required=False
                    if required_pos > 0:
                        arg_object['required'] = True
                        options = options_column[0:required_pos].rstrip()
                    arg_object['options'] = options
                    arg_object['help'] =  convert_help_column(help_column)
                    l = cmd_object['arguments'] 
                    l.append(options)
                    cmd_object['arguments'] = l 
                    cmd_object['argument_tree'][options]=arg_object
                    cmd_object['group']= get_group_name_from_command(cmd)
                    cmd_object['command']=cmd
                    cur_argument = options
                else:
                    arg_object = cmd_object['argument_tree'][cur_argument]
                    arg_object['help'] = convert_help_column("{} {}".format(arg_object['help'],l))
                    cmd_object['argument_tree'][cur_argument] = arg_object
            elif in_block_type ==IN_BLOCK_TYPE_EXAMPLES:
                cmd_object['example'] = "{}\n{}".format(cmd_object['example'],l)
            else:
                in_block_type = IN_BLOCK_TYPE_NONE ## reset
                logger.error("[Warning] OTHER::cmd:{} :: {}".format(cmd_string, l))

        # Break the loop when 
        # - buffer is empty and
        # - Popen.poll returns not None (=process terminate)
        if not line and proc.poll() is not None:
           break
    dump_cmd_object(cmd_object)
    return cmd_object

def get_group_name_from_command(cmd):
    group_name = " ".join(cmd.split()[:-1])
    if not group_name:
        group_name = 'az'
    return group_name

def get_parent_name_from_group_name(group_name):
    parent = " ".join(group_name.split()[:-1])
    if not parent and group_name != 'az':
        parent = 'az'
    return parent

## Create Group & SubGroup Tree
def get_groups(cmd_table):
    from azure.cli.core.help_files import helps
    groups_map = {}
    ## Populate group and group summary from helps
    for cmd in helps:
        diction_help = yaml.load(helps[cmd])
        if diction_help.has_key('type') and diction_help['type'] != 'group':
            continue
        group_name = cmd
        group = new_parsing_group()
        if diction_help.has_key('short-summary'):
            group['name'] = group_name
            group['summary'] = diction_help['short-summary']
            groups_map[group_name] = group
    ## Populate group from cmd table
    for cmd in cmd_table:
        group_name = get_group_name_from_command(cmd)
        if not groups_map.has_key(group_name):
            group = new_parsing_group()
            group_cmd_list = []
            group_cmd_list.append(cmd)
            group['name'] = group_name
            group['commands'].append(cmd)
            groups_map[group_name] = group
        else:
            groups_map[group_name]['commands'].append(cmd)
    return groups_map   

def LEAF_NODE(node):
    return node.split()[-1]

def LEAF_NODES(nodes):
    l=[]
    for node in nodes:
        l.append(node.split()[-1]) 
    return l

def populate_group_command_tree(group, groups_map,cmds_map):
    ## Inrease the limit just in case recursive func calling use up recursionlimit
    #import sys
    #sys.setrecursionlimit(10000)
    subgroups = []
    for subgroup_name in group['subgroups']:
        if groups_map.has_key(subgroup_name):
            subgroup = groups_map[subgroup_name]
            populate_group_command_tree(subgroup, groups_map, cmds_map)
            subgroups.append(subgroup)
    group['subgroups']=subgroups
    cmd_list = []
    for cmd_name in group['commands']:
        if cmds_map.has_key(cmd_name):
            cmd_list.append(cmds_map[cmd_name])
    group['commands']=cmd_list

def group_to_index_tree(index_tree, group_name, groups_map,cmds_map):
    index_tree['arguments'] = []
    index_tree['argument_tree'] = {}
    index_tree['summary'] = groups_map[group_name]['summary']

    child_index_tree_dict = []
    leaf_command_list = []
    # group.commands -> index_tree.commands
    leaf_command_list = LEAF_NODES(groups_map[group_name]['commands'])
    # group.commands -> index_tree.command_tree
    child_index_tree_dict = {}
    for cmd_name in groups_map[group_name]['commands']:
        child_index_tree = new_index_command_tree()
        command_to_index_tree(child_index_tree, cmd_name, cmds_map)        
        child_index_tree_dict[LEAF_NODE(cmd_name)] = child_index_tree
    # group.subgroups -> index_tree.commands + index_tree.command_tree
    for subgroup_name in groups_map[group_name]['subgroups']:
        leaf_command_list.append(LEAF_NODE(subgroup_name))
        child_index_tree = new_index_command_tree()
        group_to_index_tree(child_index_tree, subgroup_name, groups_map,cmds_map)
        child_index_tree_dict[LEAF_NODE(subgroup_name)] = child_index_tree
    
    index_tree['commands'] = leaf_command_list
    index_tree['command_tree'] = child_index_tree_dict

def command_to_index_tree(index_tree, command_name, cmds_map):
    if cmds_map.has_key(command_name):
        index_tree['arguments'] = cmds_map[command_name]['arguments']
        index_tree['argument_tree'] = cmds_map[command_name]['argument_tree']
        index_tree['commands'] = []
        index_tree['command_tree'] = {}
        index_tree['summary'] = cmds_map[command_name]['summary']

##
## Main entrypoint for Azure Shell Index Generator
##
def main():
    parser = argparse.ArgumentParser(description='Azure Shell CLI Index Generator')
    parser.add_argument(
        '-o','--output',
        help='Azure Shell index file output path (ex. /tmp/cli-index.json)')
    parser.add_argument(
        '--verbose', action='store_true',
        help='Increase verbosity')
    args = parser.parse_args()

    ## Logging config
    handler = logging.StreamHandler(sys.stdout)
    if args.verbose:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # Output file validation and config
    if not args.output:
        logger.error('[ERROR] No output file specified with -o or --output param!')
        sys.exit(1)
    output_file = os.path.abspath(args.output)
    if not os.path.isdir(os.path.dirname(output_file)):
        logger.error('[ERROR] No directory exists for output file:{}'.format(output_file))
        sys.exit(1)
 
    ## az executable command path check
    if not find_executable_path('az'):
        logger.error("[ERROR] NO azure cli (az) executable command found!")
        logger.error("Please install Azure CLI 2.0 and set its executable dir to PATH")
        logger.error("See https://github.com/Azure/azure-cli")
        sys.exit(1)

    azure_cli_version = get_cli_version()
    ## Check minimum azure-cli version
    if azure_cli_version < AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION:
        logger.error("[ERROR] Azure CLI 2.0 minimum version failure!")
        logger.error("Minimum azure-cli version required: {} (Your version: {})".format(
                    AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION, azure_cli_version))
        logger.error("Please install the latest azure-cli and set its executable dir to PATH")
        logger.error("See https://github.com/Azure/azure-cli")
        sys.exit(1)    

    ## Import Azure CLI core modules
    module_import_trial_count = 0
    while True:
        try:
            from azure.cli.core.help_files import helps
            from azure.cli.core.application import APPLICATION, Configuration
            break    
        except ImportError:
            if module_import_trial_count > 0:
                logger.error("[ERROR] azure.cli.core module import failure!")
                sys.exit(1)
            ## Getting AzureCLI modules path and append it to current path list
            azurecli_modules_path = get_azurecli_modules_path()
            if azurecli_modules_path:
                sys.path.append(azurecli_modules_path)
        module_import_trial_count = module_import_trial_count + 1

    cmd_table = APPLICATION.configuration.get_command_table()
    groups_map = {}
    cmds_map = {}
    groups_map = get_groups(cmd_table)
    ## Populate subgroups for each groups
    for group_name in groups_map.keys():
        parent_name = get_parent_name_from_group_name(group_name)
        if parent_name:
            groups_map[parent_name]['subgroups'].append(group_name)

    logger.info("Start generating index...")
    logger.info("Output index file: {}".format(output_file))

    ## Get command list
    cmd_list = cmd_table.keys()
    for cmd in cmd_list:
        try:
            cmds_map[cmd] = capture_cmd(cmd)
        except:
            pass

    ## Create Json Tree from root 'az' group
    index_tree = new_index_command_tree()
    group_to_index_tree(index_tree, 'az', groups_map,cmds_map)
    root_tree = {'az': index_tree}
    result_json = json.dumps(root_tree)
    
    ## Write json to your specified output file
    with open(output_file, "w") as f:
        f.write(result_json)
