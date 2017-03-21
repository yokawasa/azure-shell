# -*- coding: utf-8 -*- 

from __future__ import print_function, unicode_literals

import os
import sys
import argparse

from .azureshell import AzureShell
from .completer import AzureShellCompleter
from .index import AzureShellIndex, AzureShellIndexException
from .config import AzureShellConfig
from .cache import AzureShellCache
from .utils import get_cli_version, find_executable_path, AS_ERR, AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION
from .logger import init_logger

__version__ = '0.2.0'
_DEFAULT_AZURE_SHELL_BASE_DIR = '{}/.azureshell'.format(os.environ['HOME'])

def main():

    parser = argparse.ArgumentParser(description='An interactive Azure CLI command line interface')
    parser.add_argument(
        '--version', action='version', version=__version__)
    parser.add_argument(
        '--basedir',
        help='Azure Shell base dir path ($HOME/.azureshell by default)')
    parser.add_argument(
        '--config',
        help='Azure Shell config file path ($HOME/.azureshell/azureshell.conf by default)')
    parser.add_argument(
        '--index',
        help='Azure Shell index file to load ($HOME/.azureshel/cli-index-<azure_cli_version>.json)')
    args = parser.parse_args()

    ## az executable command path check
    if not find_executable_path('az'):
        AS_ERR("[ERROR] NO azure cli (az) executable command found!")
        AS_ERR("Please install Azure CLI 2.0 and set its executable dir to PATH")
        AS_ERR("See https://github.com/Azure/azure-cli")
        sys.exit(1)
    
    azure_cli_version = utils.get_cli_version()
    ## Check minimum azure-cli version
    if azure_cli_version < AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION:
        AS_ERR("[ERROR] Azure CLI 2.0 minimum version failure!")
        AS_ERR("Minimum azure-cli version required: {} (Your version: {})".format(
                    AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION, azure_cli_version))
        AS_ERR("Please install the latest azure-cli and set its executable dir to PATH")
        AS_ERR("See https://github.com/Azure/azure-cli")
        sys.exit(1)

    print("azure-shell version:{}".format(__version__))
    #print("AzureCLI version:{}".format(azure_cli_version))

    base_dir = args.basedir if args.basedir else _DEFAULT_AZURE_SHELL_BASE_DIR
    config_file = args.config if args.config else '{}/azureshell.conf'.format(base_dir)
    config = None
    ## Check if config file exists
    if not os.path.exists(config_file):
        AS_ERR("[WARNING] No config file found:{}".format(config_file))
        AS_ERR("Creating an default config file :{}".format(config_file))
        AzureShellConfig.makedefaultconfig(config_file)
    config = AzureShellConfig(config_file)
    init_logger('azureshell', config.log_file, config.log_level)

    index = AzureShellIndex(base_dir)
    index_file = ''
    index_version = ''
    if args.index:
        index_file = args.index
        # Check if specified index file exists and exit if the file does not exist
        if not os.path.exists(index_file):
            AS_ERR("[ERROR] index file doesn't exist: {}".format(index_file))
            sys.exit(1)
    else:
        # Check if default index file exists and download the file if not exist on local
        index_version = index.get_local_version()
        index_file = index.get_index_file(index_version)
        if not index_version or \
                not os.path.exists(index_file) or index_version < azure_cli_version:
            index = AzureShellIndex(base_dir)
            index_version = index.download_index_from_repository(azure_cli_version)
            index_file = index.get_index_file(index_version)

    AzureShellCache.Instance().set('base_dir', base_dir)
    AzureShellCache.Instance().set('index_file', index_file)
    AzureShellCache.Instance().set('config_file',config_file)

    index_data = {}
    try:
        index_data = AzureShellIndex.load_index(index_file)
    except AzureShellIndexException as e:
        AS_ERR("[ERROR] index file loading failure: {}".format(index_file))
        AS_ERR(str(e))
        sys.exit(1)

    completer = AzureShellCompleter(index_data)
    azureshell = AzureShell(config,completer)
    azureshell.run()

if __name__ == '__main__':
    main()
