# -*- coding: utf-8 -*- 

import os
import json
import logging
import urllib2
from . import utils

logger = logging.getLogger('azureshell.index')

_AZURE_SHELL_REMOTE_URL_BASE = "https://azureshellrepo.blob.core.windows.net/index"
_AZURE_SHELL_AVAILABLE_INDEX_FILE = "index.available"
_AZURE_SHELL_LOCAL_INDEX_VERSION_FILE = "index.local"

class AzureShellIndexException(Exception):
    pass

class AzureShellIndex(object):

    def __init__(self, index_base_dir):
        self._index_base_dir = index_base_dir
        self._version_file = "{}/{}".format(index_base_dir, _AZURE_SHELL_LOCAL_INDEX_VERSION_FILE)
    
    def get_index_file(self, index_version):
        return "{}/cli-index.{}.json".format(self._index_base_dir, index_version)

    def get_local_version(self):
        if not os.path.exists(self._version_file):
            return None
        f = open(self._version_file)
        v = f.readline().strip()
        f.close
        return v

    def set_local_version(self,index_version):
        f = open(self._version_file,"w")
        f.writelines(str(index_version))
        f.close

    def download_index_from_repository(self, index_version ):
        # Check available list and get the best version
        version_to_download = AzureShellIndex.get_best_index_version_in_repository(index_version)
        local_index_version = self.get_local_version()
        # Download index if needed
        if not local_index_version or version_to_download > local_index_version:
            if not os.path.isdir(self._index_base_dir):
                os.makedirs(self._index_base_dir)
            remote_url = "{}/cli-index.{}.json".format(
                _AZURE_SHELL_REMOTE_URL_BASE,version_to_download)
            logger.debug("Downloading...:{}".format(remote_url)) 
            f = urllib2.urlopen(remote_url)
            data = f.read()
            local_index_file = "{}/cli-index.{}.json".format(self._index_base_dir, version_to_download)
            with open(local_index_file, "wb") as code:
                code.write(data)

            ## Update local index version
            self.set_local_version(version_to_download)
        return version_to_download

    def load(self, index_version):
        index_file = "{}/cli-index.{}.json".format(self._index_base_dir, index_version)
        return AzureShellIndex.load_index(index_file)

 
    ### TODO: error handling
    @staticmethod
    def get_best_index_version_in_repository( index_version ):
        # Check available list and get the best version
        remote_url = "{}/{}".format(
            _AZURE_SHELL_REMOTE_URL_BASE, _AZURE_SHELL_AVAILABLE_INDEX_FILE)
        logger.debug("Reading...:{}".format(remote_url)) 
        f = urllib2.urlopen(remote_url)
        data = f.read()
        versions=data.splitlines()
        versions.sort(reverse=True)
        ## check if versions contains myversion
        my_nearest_version = index_version
        if not index_version in versions:
            ## get my nearest available version if not versions contains index_version
            for i in versions:
                if index_version > i:
                    my_nearest_version = i
                    break
        return my_nearest_version
    
    @staticmethod
    def load_index(index_file):
        if not os.path.exists(index_file):
            estr="index file does not exist:{}".format(index_file)
            logger.error(estr)
            raise AzureShellIndexException(estr)

        data = {}
        try:
            with open(index_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(str(e))
            raise AzureShellIndexException(str(e))
        return data


def _parse_command(name, command_obj,completions):
    if not command_obj:
        return
    if command_obj.has_key('arguments'):
        args = command_obj['arguments']
        for arg in args:
            options = arg.split()
            completions['args'].update(options)
    if command_obj.has_key('commands') and command_obj.has_key('command_tree'):
        subcommand_names = command_obj['commands']
        completions['commands'].extend(subcommand_names)
        cmd_tree = command_obj['command_tree']
        for subcommand_name in cmd_tree.keys():
            subcommand_obj = cmd_tree[subcommand_name]
            _parse_command(subcommand_name, subcommand_obj,completions)

def get_completions_commands_and_arguments( index_data = {} ):
    completions = {
        'commands': [],
        'args': set()
    }
    index_root = index_data['az']
    completions['commands'] = index_root['commands']
    for command_name in completions['commands']:
        command_obj = index_root['command_tree'].get(command_name)
        _parse_command(command_name, command_obj, completions)
    return completions
