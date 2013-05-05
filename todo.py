#!/usr/bin/env python
# coding=utf8

__version__ = '0.1.1'


from ply import lex
from ply import yacc


class TodoLexer(object):

    tokens = (
        "ID",
        "TAG",
        "STATUS",
        "TASK",
    )

    t_ignore = "\x20\x09"  # ignore spaces and tabs
    t_ignore_COMMENT = r'\#.*'  # comments

    def t_ID(self, t):
        r'\#\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
        t.value = int(t.value[1:])
        return t

    def t_TAG(self, t):
        r'-+(.*)-+'
        t.value = ''.join(i for i in t.value if i != '-')
        t.value = t.value.strip()
        return t

    def t_STATUS(self, t):
        r'(\(done\))|(\(undone\))'
        t.value = (t.value == "(done)")
        return t

    def t_TASK(self, t):
        r'(.(?!\(done\))(?!\(undone\)))*\S'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise SyntaxError(
            "Illegal character: '%s' at Line %d" % (t.value[0], t.lineno)
        )

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            print tok

lexer = TodoLexer()
lexer.test(open("todo.txt").read())

