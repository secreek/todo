#!/usr/bin/env python
# coding=utf8

__version__ = '0.1.1'

import os
from os.path import expanduser
from ply import lex
from ply import yacc


class Task(object):
    """
    Task object.
    One task looks like

      1. (x) Go shopping

    if not done,  leave there blank.

    Attributes
      id          int     task's id
      content     str     task'content
      done        bool    is this task done?
    """
    def __init__(self, id, content, done=False):
        self.id = id
        self.content = content
        self.done = done


class Todo(list):
    """
    A todo is kind of a list of tasks.
    """
    pass


class TodoLexer(object):
    """
    Lexer for Todo format string.
    Tokens
      ID        e.g. '1.'
      DONE      e.g. '(x)'
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
        r'(\(x\))'
        return t

    def t_TASK(self, t):
        r'((?!\(x\))).+'
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


class TodoGenerator(object):
    """
    Generator from python list to string.
    """

    g_newline = "\n"

    def g_id(self, v):
        return str(v) + "."

    def g_done(self, v):
        if v is True:
            return '(x)'
        else:
            return '   '

    def g_task(self, v):
        return v

    def gen_task(self, task):
        lst = []
        lst.append(self.g_id(task.id))
        lst.append(self.g_done(task.done))
        lst.append(self.g_task(task.content))
        return " ".join(lst)

    def generate(self, todo):
        """
        Generate todo to string format.

        todo    kind of a list of tasks, instance of class Todo

        e.g.
          [<task object>, ..] => "1. (x) do something .."
        """
        re = []
        for i in todo:
            if isinstance(i, Task):
                re.append(self.gen_task(i))
            else:
                raise SyntaxError('Not support type: ' + type(i))
        return self.g_newline.join(re)


lexer = TodoLexer()  # build lexer
parser = TodoParser()  # build parser
generator = TodoGenerator()  # build generator


class TodoApp(object):
    """
    Todo application.

    Use which file for storage?
      if "./todo.txt" exists, use it. else use "~/todo.txt" instead.
      if both two paths not exist, touch one in "~" directory.
    """

    def __init__(self):
        self.tasks = self.parse_from_file()

    def file_path(self):
        # find the file's path to use
        fn = "todo.txt"
        home = expanduser("~")
        home_fn = os.path.join(home, fn)
        open(home_fn, "a").close()  # touch if not exists

        if os.path.exists(fn):
            return fn
        else:
            return home_fn

    def parse_from_file(self):
        """
        read todos from file.
        return the tasks of "todo.txt".
        """
        content = open(self.file_path()).read()
        return parser.parse(content)

    def generate_to_file(self, tasks):
        """
        generate tasks to file.
        """
        content = generator.generate(tasks)
        open(self.file_path(), "w").write(content)


s  = open("/home/hit9/todo.txt").read()

for task in parser.parse(s):
    print task.content
