#!/usr/bin/env python
# coding=utf8
"""
Usage:
  test.py [-h|-v|-a]
  test.py clear
  test.py (<id> [done|undone])|<task>...

Options:
  -h --help      show this message
  -v --version   show version
  -a --all       show all

Examples:
  Add a task                    todo Go shopping!
  Check a task as done          todo 1 done
  Check a task as undone        todo 1 undne
  Print all tasks               todo --all
  Print undone tasks            todo
"""

__version__ = '0.1.1'

import os
from ply import lex
from ply import yacc
from os.path import expanduser
from termcolor import colored


class Task(object):
    """
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

    Methods here
      next_id()                 return the next id should be.
      new_task(content)         new an undone task from content
      clear()                   clear this todo
    """

    def next_id(self):
        """
        Return next id by auto_increment rule.
        """
        ids = [task.id for task in self]
        max_id = max(ids) if ids else 0
        return (max_id + 1)

    def new_task(self, content):
        """
        Append a undone task by content
        """
        task = Task(self.next_id(), content, False)
        return self.append(task)

    def check_task(self, id):
        """
        Check task's status to done.
        """
        self.get_task(id).done = True

    def undo_task(self, id):
        """
        Undone some task.
        """
        self.get_task(id).done = False

    def get_task(self, id):
        """
        Get task by id from todo.
        """
        for task in self:
            if task.id == id:
                return task
        return None

    def clear(self):
        """
        Clear all tasks!
        """
        self[:] = []


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


class TodoApp(object):
    """
    Todo application.

    Use which file for storage?
      if "./todo.txt" exists, use it. else use "~/todo.txt" instead.
      if both two paths not exist, touch one in "~" directory.
    """

    lexer = TodoLexer()  # build lexer
    parser = TodoParser()  # build parser
    generator = TodoGenerator()  # build generator

    def __init__(self):
        self.todo = self.parse_from_file()

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
        return self.parser.parse(content)

    def generate_to_file(self):
        """
        generate tasks to file.
        """
        content = self.generator.generate(self.todo)
        open(self.file_path(), "w").write(content)

    def print_task(self, task):
        """
        print single task to screen.
        """
        status = colored('✓', 'green') if task.done else colored('✖', 'red')
        print str(task.id) + '.' + ' ' + status + ' ' + task.content

    def print_task_by_id(self, id):
        """
        print single task by its id.
        """
        self.print_task(self.todo.get_task(id))

    def ls_tasks(self):
        """
        ls all tasks ouput to screen.
        """
        for task in self.todo:
            self.print_task(task)

    def ls_undone_tasks(self):
        """
        ls all undone tasks
        """
        for task in self.todo:
            if not task.done:
                self.print_task(task)

    def ls_done_tasks(self):
        """
        ls all done tasks
        """
        for task in self.todo:
            if task.done:
                self.print_task(task)

    def check_task(self, id):
        """
        Check one task to done.
        """
        self.todo.check_task(id)
        self.generate_to_file()

    def undo_task(self, id):
        """
        Check one task to undone.
        """
        self.todo.undo_task(id)
        self.generate_to_file()

    def clear_tasks(self):
        """
        Clear todo!
        """
        self.todo.clear()
        self.generate_to_file()

    def add_task(self, content):
        """
        Add new task.
        """
        self.todo.new_task(content)
        self.generate_to_file()

    def run(self):
        """
        Get arguments from cli and run!
        """
        from docopt import docopt
        args = docopt(__doc__, version=__version__)

        if args["clear"]:
            self.clear_tasks()
        elif args["<id>"]:
            try:
                id = int(args["<id>"])

                if args["done"]:
                    self.check_task(id)
                elif args["undone"]:
                    self.undo_task(id)
                else:
                    self.print_task_by_id(id)
            except ValueError:  # if not an integer format str, regard as a task
                self.add_task(args["<id>"])
        elif args["<task>"]:
            self.add_task(" ".join(args["<task>"]))
        elif args["--all"]:
            self.ls_tasks()
        else:
            self.ls_undone_tasks()


if __name__ == '__main__':
    app = TodoApp()
    app.run()
