# -*- coding: utf-8 -*-

from pygments.lexer import words
from pygments.lexer import RegexLexer
from pygments.token import Text, Keyword, Literal, Name, Operator
from .index import AzureShellIndex, get_completions_commands_and_arguments
from .cache import AzureShellCache

class AzureShellLexer(RegexLexer):
    index_data = {}
    index_data = AzureShellIndex.load_index( AzureShellCache.Instance().get('index_file'))
    completions = get_completions_commands_and_arguments(index_data)

    tokens = {
        'root': [
            (words( tuple(['az']), prefix=r'\b', suffix=r'\b'), Literal.String),
            (words( tuple(completions['commands']), prefix=r'\b', suffix=r'\b'), Name.Class),
            (words( tuple(list(completions['args'])), prefix=r'', suffix=r'\b'), Keyword.Declaration),
            # Everything else
            (r'.*\n', Text),
        ]
    }
