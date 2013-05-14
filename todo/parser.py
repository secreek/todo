# coding=utf8
# _____      _________
# __  /____________  /_____
# _  __/  __ \  __  /_  __ \
# / /_ / /_/ / /_/ / / /_/ /
# \__/ \____/\__,_/  \____/
#
# Todo application in the command line, with readable storage.
# Authors: https://github.com/secreek
# Home: https://github.com/secreek/todo
# Email: nz2324@126.com
# License: MIT

"""
  Parse todo.txt to python's object <Todo>.

  To parse string to <Todo instance>::

      parser.parse(string)  # return <Todo instance>

  What the todo format is? A todo is made up of name and tasks.
  A sample looks like::

    Todo's name
    ------------

    - [x] Here is todo's task

    -     And another task

  As you see, the format of todo string is obvious and readable. The string
above maps to a <Todo> instance, like a list.

"""

from models import Todo
from models import Task

from ply import lex
from ply import yacc


class TodoSyntaxError(Exception):
    """
      Raised when syntax errors occurred.
    """
    pass


class Lexer(object):  # really a simple parser, ha?
    """
      Lexer for todo.txt

      Tokens
        TASK    => Task     e.g. '- [x] task..'
        NAME    => str      e.g. 'TodoName\n-------'

      To use the lexer::
          lexer = Lexer()
    """

    tokens = ("TASK", "NAME")

    t_ignore = " \t"  # ignore spaces and tabs

    def __init__(self):
        # the lexer built with instance
        self.lexer = lex.lex(module=self)

    def t_TASK(self, t):
        r'-\s+(?P<done>\[x\])?\s+(?P<content>.+)'
        content = t.lexer.lexmatch.group('content')
        done = True if t.lexer.lexmatch.group('done') else False
        t.value = Task(content=content, done=done)
        return t

    def t_NAME(self, t):
        r'(?P<name>[^\n]+)\n\s*-{3,}\s*\n*'
        t.value = t.lexer.lexmatch.group('name')  # todo's name
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise TodoSyntaxError(
            "Illegal character '%s' at Line %d" % (t.value[0], t.lineno)
        )

    def test(self, data):
        # test lexer
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print tok


class Parser(object):
    """
      Parser for todo.txt, works with a lexer.

      e.g.::
          parser = Parser()
          parser.parse(string)
    """

    tokens = Lexer.tokens

    def __init__(self):
        self.parser = yacc.yacc(module=self, debug=0, write_tables=0)

    def parse(self, data):
        """
          Parse todo.txt to todo instance.

          parameters
            data        str     todo format string
          return <Todo>
        """
        self.todo = Todo()  # reset todo
        return self.parser.parse(data)

    def p_error(self, p):
        if p:
            raise TodoSyntaxError(
                "Character '%s' at line %d" % (p.value[0], p.lineno)
            )
        else:
            raise TodoSyntaxError("SyntaxError at EOF")

    def p_start(self, p):  # parser start here
        "start : translation_unit"
        p[0] = self.todo

    def p_translation_unit(self, p):  # translate all
        """
        translation_unit : translation
                         | translation_unit translation
                         |
        """
        pass

    def p_translation_name(self, p):
        """
        translation : NAME
        """
        if self.todo.name:
            raise TodoSyntaxError('Duplicate definition of todo\'s name')
        self.todo.name = p[1]

    def p_translation_task(self, p):  # translate token TASK
        """
        translation : TASK
        """
        self.todo.tasks.append(p[1])


lexer = Lexer()
parser = Parser()  # build parser
