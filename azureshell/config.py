# -*- coding: utf-8 -*-

import os
from ConfigParser import SafeConfigParser, NoOptionError

_DEFAULT_AZURE_SHELL_CONFIG_HIGHLIGHTER_STYLE = 'vim'
_DEFAULT_AZURE_SHELL_CONFIG_LOG_FILE = '~/azureshell.log'
_DEFAULT_AZURE_SHELL_CONFIG_LOG_LEVEL = 'INFO'

class AzureShellConfig(object):

    def __init__(self, config_file=None):
        self._config_file = config_file
        self._config_parser = SafeConfigParser()

        if self._config_file:
            self._config_parser.read(config_file)

    @staticmethod
    def makedefaultconfig(config_file):
        dir_name = os.path.dirname(config_file)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        with open(config_file, "w") as f:
            f.write("[azureshell]\n# Pygments: highlighter style\n# run ./scripts/get-styles.py\n# 'manni', 'igor', 'lovelace', 'xcode', 'vim', 'autumn', 'abap', 'vs', 'rrt', 'native', 'perldoc', 'borland', 'arduino', 'tango', 'emacs', 'friendly', 'monokai', 'paraiso-dark'\n# To disable themes, set highlighter_style = none\nhighlighter_style = vim\n\n# log_file location\nlog_file = ~/.azureshell/azureshell.log\n\n# Default log level. Possible values: 'CRITICAL', 'ERROR', 'WARNING', 'INFO' and 'DEBUG'\nlog_level = DEBUG")

    def _get_string(self, section, key, default_val):
        v =''
        if not self._config_file:
            return default_val

        try:
            v = self._config_parser.get(section, key)
        except NoOptionError as e:
            v = default_val
        return v

    @property
    def highlighter_style(self):
        return self._get_string('azureshell','highlighter_style',_DEFAULT_AZURE_SHELL_CONFIG_HIGHLIGHTER_STYLE)
       
    @property
    def log_file(self):
        return self._get_string('azureshell','log_file',_DEFAULT_AZURE_SHELL_CONFIG_LOG_FILE)
    
    @property
    def log_level(self):
        return self._get_string('azureshell','log_level',_DEFAULT_AZURE_SHELL_CONFIG_LOG_LEVEL)
