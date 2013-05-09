# coding=utf8

"""
Parser to parse todo format string to todo object.
"""

from models import Task
from models import Todo

import re
from ply import lex
from ply import yacc


class Lexer(object):
    """
    Lexer for todo format string

    Tokens
      ID        e.g. '1.'
      DONE      e.g. '[x]'
      TASK      e.g. 'This is a sample task'
    """

    tokens = (
        "ID",
        "DONE",
        "TASK",
    )

    t_ignore = "\x20\x09"  # space & tab

    def __init__(self):
        # the lexer built with instance
        self.lexer = lex.lex(module=self)

    def t_ID(self, t):
        r'\d+\.([uU]|[lL]|[uU][lL]|[lL][uU])?'
        t.value = int(t.value[:-1])
        return t

    def t_DONE(self, t):
        r'(\[x\])'
        return t

    def t_TASK(self, t):
        r'((?!\[x\])).+'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise SyntaxError("Illegal character '%s' at Line %d" % (t.value[0], t.lineno))


class Parser(object):
    """
    Parser for todo format string, works with a lexer.

    e.g.

      parser = Parser()
      parser.parse(string)  # return a todo instance
    """

    tokens = Lexer.tokens

    seperator_re = re.compile("\s*-+\s*")

    def p_error(self, p):
        if p:
            raise SyntaxError("Character '%s' at line %d" % (p.value[0], p.lineno))
        else:
            raise SyntaxError("SyntaxError at EOF")

    def p_start(self, p):
        "start : translation_unit"
        p[0] = self.todo

    def p_translation_unit(self, p):
        """
        translation_unit : translate_task
                         | translation_unit translate_task
                         |
        """
        pass

    def p_translation_task(self, p):
        """
        translate_task : ID DONE TASK
                       | ID TASK
        """
        if len(p) == 4:
            done = True
            content = p[3]
        elif len(p) == 3:
            done = False
            content = p[2]

        task = Task(p[1], content, done)
        # Note: this not new_task, but a task exist
        # should be append to list directly
        self.todo.tasks.append(task)

    def __init__(self):
        self.parser = yacc.yacc(module=self, debug=0, write_tables=0)

    def parse(self, data):
        """
        Parse todo content to todo instance.

        parameter
          data      str     todo format string
        """
        data = data.strip()  # remove empty lines

        lines = data.splitlines()
        seperator_line = None

        for lineno, line in enumerate(lines):
            if self.seperator_re.match(line):
                seperator_line = lineno
                break  # find the first seperator

        if seperator_line != None:
            name = "\n".join(lines[:seperator_line]).strip()
            body = "\n".join(lines[seperator_line + 1:])
        else:
            name = None
            body = "\n".join(lines)

        self.todo = Todo(name=name)  # reset todo instance
        return self.parser.parse(body)


lexer = Lexer()
parser = Parser()
