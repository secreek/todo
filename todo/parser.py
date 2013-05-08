# coding=utf8

"""
Parser for todo format string.
"""

from models import Task
from models import Todo

from ply import lex
from ply import yacc


class TodoLexer(object):
    """
    Lexer for Todo format string.
    Tokens
      ID        e.g. '1.'
      DONE      e.g. '[x]'
      TASK      e.g. 'This is a task'
    """

    tokens = (
        "ID",
        "DONE",
        "TASK",
    )

    t_ignore = "\x20\x09"  # ignore spaces and tabs

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
        raise SyntaxError(
            "Illegal character: '%s' at Line %d" % (t.value[0], t.lineno)
        )

    def __init__(self):
        self.lexer = lex.lex(module=self)


class TodoParser(object):
    """
    Parser for Todo format string, works with a todo lexer.

    Parse string to Python list
      todo_str = "1. (x) Write email to tom"
      TodoParser().parse(todo_str)
    """

    tokens = TodoLexer.tokens

    def p_error(self, p):
        if p:
            raise SyntaxError(
                "Character '%s' at line %d" % (p.value[0], p.lineno)
            )
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
        self.todo.append(task)

    def __init__(self):
        self.parser = yacc.yacc(module=self, debug=0, write_tables=0)

    def parse(self, data):
        # reset list
        self.todo = Todo()
        return self.parser.parse(data)


lexer = TodoLexer()  # build lexer
parser = TodoParser()  # build parser
