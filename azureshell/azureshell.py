# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import sys
import subprocess
import logging

from prompt_toolkit.document import Document
from prompt_toolkit.shortcuts import create_eventloop,create_default_layout
from prompt_toolkit.layout.processors import HighlightMatchingBracketProcessor, ConditionalProcessor
from prompt_toolkit.filters import Always, HasFocus, IsDone
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.interface import CommandLineInterface, Application, AbortAction, AcceptAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory, FileHistory
from prompt_toolkit.key_binding.manager import KeyBindingManager
from pygments.token import Token
from pygments.util import ClassNotFound
from pygments.styles import get_style_by_name
from prompt_toolkit.styles import default_style_extensions, style_from_dict

from .cache import AzureShellCache

logger = logging.getLogger('azureshell.azureshell')

class InputInterrupt(Exception):
    pass

class AzureShell(object):

    def __init__(self, config, completer):
        self._cli = None
        self._env = os.environ.copy()
        self.history = InMemoryHistory()
        self.file_history = FileHistory(
                "{}/history".format(AzureShellCache.Instance().get('base_dir')))
        self._config = config
        self.completer = completer

    def run(self):
        while True:
            try:
                document = self.get_cli().run(reset_current_buffer=True)
                text = document.text
            except InputInterrupt:
                pass
            except (KeyboardInterrupt, EOFError):
                logger.debug("breaking loop due to KeyboardInterrupt or EOFError")
                break
            else:
                if text.startswith('exit') or text.startswith('quit'):
                    sys.exit(0)

                if text.startswith('az'):
                    full_cmd = text
                    self.history.append(full_cmd)
                else:
                    full_cmd = text[0:]
                
                logger.debug("Execute subprocess command:{}".format(full_cmd))
                self.get_cli().request_redraw()
                p = subprocess.Popen(full_cmd, shell=True, env=self._env)
                p.communicate()

    def on_input_timeout(self, cli):
        document = cli.current_buffer.document
        text = document.text
        logger.debug("on_input_timeout document:{}".format(document))
        # Add 'az' to current buffer if no text typed in
        #if not document.text:
        #    cli.current_buffer.document = Document(u'az', 2)
        cli.request_redraw()

    def get_cli(self):
        if self._cli is None:
            self._cli = self.create_cli()
        return self._cli

    def create_cli(self):
        ## KeyBindings configuration
        key_binding = KeyBindingManager(
            enable_search=True,
            enable_abort_and_exit_bindings=True,
            enable_system_bindings=True,
            enable_auto_suggest_bindings=True,
            enable_open_in_editor=False)

        ## Buffer configuration
        default_buffer= Buffer(
            history=self.file_history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
            completer=self.completer,
            complete_while_typing=Always(),
            accept_action=AcceptAction.RETURN_DOCUMENT)

        ## Style configuration
        try:
            style = get_style_by_name(self._config.highlighter_style)
        except ClassNotFound:
            style = get_style_by_name('native')

        styles = {}
        styles.update(style.styles)
        styles.update(default_style_extensions)
        styles.update({
            Token.Menu.Completions.Completion: 'bg:#003fff #ffffff',
            Token.Menu.Completions.Completion.Current: 'bg:#5ab300 #000000',
            Token.Menu.Completions.Meta.Current: 'bg:#5ab300 #ffffff',
            Token.Menu.Completions.Meta: 'bg:#ffffff #000000',
            Token.Scrollbar: 'bg:#003fff',
            Token.Scrollbar.Button: 'bg:#003333',
        })
        prompt_style = style_from_dict(styles)

        ## Application
        application = Application(
            layout=self.create_cli_layout(),
            mouse_support=False,
            style=prompt_style,
            buffer=default_buffer,
            on_abort=AbortAction.RETRY,
            on_exit=AbortAction.RAISE_EXCEPTION,
            on_input_timeout=self.on_input_timeout,
            key_bindings_registry=key_binding.registry,
        )

        cli = CommandLineInterface(application=application,
                                eventloop=create_eventloop())
        return cli

    def create_cli_layout(self):
        from .lexer import AzureShellLexer
        lexer = AzureShellLexer
        return create_default_layout (
                message =u'azure> ',
                reserve_space_for_menu=8,
                lexer=lexer,
                extra_input_processors=[
                    ConditionalProcessor(
                        processor=HighlightMatchingBracketProcessor(chars='[](){}'),
                        filter=HasFocus(DEFAULT_BUFFER) & ~IsDone())
                ]                 
            ) 
