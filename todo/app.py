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

__version__ = '0.3.0'

from models import Task
from models import Todo

from parser import parser
from generator import generator

from utils import log
from utils import colored
from utils import ask_input

import os


class File(object):
    """File object to manage io with disk"""

    home = os.path.expanduser("~")

    def __init__(self, path):
        self.path = path

    def read(self):
        """Read from file return the content"""
        return open(self.path).read().strip()

    def write(self, content):
        """Write string to this file"""
        return open(self.path, 'w').write(content.strip())


class TodoTxt(File):
    """
      Object to manage todo.txt's IO.

      attributes
        path    str     todo.txt's filepath
      methods
        read    read from todo.txt, return str
        write   write str to todo.txt
    """

    def __init__(self):
        """ Use './todo.txt' prior to '~/todo.txt' for persistent storage."""

        filename = "todo.txt"

        current_path = os.path.join(".", filename)
        home_path = os.path.join(self.home, filename)

        if os.path.exists(current_path):
            path = current_path
        else:
            # touch the '~/todo.txt' if it not exists
            open(home_todo_txt, "a").close()
            path = home_path

        super(TodoTxt, self).__init__(path)


class App(object):
    """
      Todo command line application.
      ::

          app = App()
          app.run()

    """

    def __init__(self):
        self.todo_txt = t = TodoTxt()  # <TodoTxt instance>
        self.todo_content = c = t.read()  # todo.txt's content
        self.todo = parser.parse(c)  # <Todo instance>

    def generate_to_txt(func):
        """
          Decorator, generate <Todo instance> to str, and then
        save to todo.txt.
        """
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.todo_txt.write(generator.generate(self.todo))
        return wrapper

    def wrap_task(self, task, index=None):
        """wrap task to colored str"""
        if task.done:
            state = colored('✓', 'green')
        else:
            state = colored('✖', "red")

        content = colored(task.content, "gray")
        wrapped_task = state + "  " + content
        if index:
            wrapped_task = colored(str(index)+'.', 'gray') + ' ' + wrapped_task
        return wrapped_task

    def wrap_todo_name(self, underline=False):
        """Wrap todo's name"""
        name = self.todo.name
        if name:
            wrapped_name = colored(name, 'orange')
            if underline:
                wrapped_name += '\n' + colored(len(name) * '-', 'gray')
            return wrapped_name
        return None

    def ls_tasks(self, filter_func=None):
        """ls tasks by filter"""

        tasks = filter(filter_func, self.todo.tasks)
        print self.wrap_todo_name(underline=True)  # print name
        for index, task in enumerate(tasks, 1):
            print self.wrap_task(task, index)
