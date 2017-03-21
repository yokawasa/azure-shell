# -*- coding: utf-8 -*- 

from __future__ import unicode_literals
import os
import logging
from prompt_toolkit.completion import Completer, Completion

logger = logging.getLogger('azureshell.completer')

class AzureShellCompleter(Completer):

    def __init__(self, index_data):
        self._index = index_data
        self._root_name = 'az'
        self._current_name = ''
        self._current = self._index[self._root_name]
        self._last_position = 0
        self._current_line = ''
        self._last_option = ''
        self.cmd_path = [self._current_name]
 
    @property
    def last_option(self):
        return self._last_option

    @property
    def current_command(self):
        return u' '.join(self.cmd_path)

    def get_completions(self, document, complete_event):
        cursor = document.text_before_cursor
        stripped_cursor = cursor.strip()
        logger.debug("get_completions cursor:{}".format(cursor))
        
        # Skip _autocomplete if user typed in NON 'az' command
        if stripped_cursor and  not stripped_cursor.startswith('az'):
            # Skip except the case that stripped_cursor is 'a'
            if not stripped_cursor =='a':
                return

        completions = self._autocomplete(cursor)
        prompt_completions = []
        word_before_cursor = ''
        if stripped_cursor:
            word_before_cursor = stripped_cursor.split()[-1]
        for completion in completions:
            arg_tree = self._current.get('argument_tree', {})
            if completion.startswith('--') and completion in arg_tree:
                meta = arg_tree[completion]
                if meta['required']:
                    display_text = '%s (required)' % completion
                else:
                    display_text = completion
                display_meta = arg_tree[completion].get('help','')
            elif completion == 'az':
                display_text = completion
                display_meta = ''
            else:
                cmd_tree = self._current.get('command_tree',{})
                display_text = completion
                display_meta = cmd_tree[completion].get('summary','')
            if cursor and cursor[-1] == ' ':
                location = 0
            else:
                location = -len(word_before_cursor)
            # Converting multiple options like '--help -h' into single 
            # like '--help' for usability
            normalized_completion = completion.split()[0] 
            prompt_completions.append ( 
                    Completion(normalized_completion, location,
                             display=display_text, display_meta=display_meta)
                )

        for c in prompt_completions:
            yield c

    def _autocomplete(self, line):
        current_length = len(line)
        self._current_line = line
        logger.debug("_autocomplete cur_line:{} (cur_len:{}, last_pos:{})".format(self._current_line, current_length, self._last_position))
        if current_length == 1 and self._last_position > 1:
            self._reset()
        elif current_length < self._last_position:
            # Hit backspace, and handling backspace
            return self._handle_backspace()
        elif not line:
            return []
        #elif current_length != self._last_position + 1:
        #    return self._complete_from_full_parse()
        
        # Only update the _last_position after the cases above were verified
        self._last_position = len(line)

        # Autocomplete with 'az' if line is a single space or 'a' 
        # (assuming that user hits a space on a new line or typed in 'a')
        stripped_line = line.strip()
        if line and ( not stripped_line or stripped_line == 'a' ):
            return ['az']
        
        # Skip if it's only space ' '
        words = line.split()
        if (len(words) < 1):
            return []
        # Now you have at least single word in the line like
        # azure> az 
        # azure> az vm
        # azure> az vm list ..
        last_word = words[-1]
        logger.debug("_autocomplete last_word: {}".format(last_word))
        if last_word in self._current.get('argument_tree', {}):
            # The last thing we completed was an argument, record this as self.last_arg
            self._last_option = last_word
        if line[-1] == ' ':
            # this is the case like:
            # 'az vm ' or 'az vm --debug '
            # 1. 'az vm '
            #    Proceed next command completions if the command has childres
            # 2. 'az vm --debug ' ( current command is 'az vm' )
            #    Process the current command completion
            if not last_word.startswith('-'):
                next_command = self._current['command_tree'].get(last_word)
                if next_command is not None:
                    self._current = next_command
                    self._current_name = last_word
                    self.cmd_path.append(self._current_name)
            return self._current['commands'][:]

        elif last_word.startswith('-'):
            all_args = self._current['arguments'] 
            # Select args with Forward matching
            return [arg for arg in sorted(all_args) if arg.startswith(last_word)]

        logger.debug("_autocomplete dump: {}".format([cmd for cmd in sorted(self._current['commands']) if cmd.startswith(last_word)]))
        # Select commands with Forward matching
        return [cmd for cmd in sorted(self._current['commands']) if cmd.startswith(last_word)]

    def _reset(self):
        self._current_name = self._root_name
        self._current = self._index[self._root_name]
        self._last_position = 0
        self._last_option = ''
        self.cmd_path = [self._current_name]

    def _handle_backspace(self):
        # reseting and starting from the beginning
        self._reset()
        line = self._current_line
        for i in range(1, len(self._current_line)):
            self._autocomplete(line[:i])
        return self._autocomplete(line)
