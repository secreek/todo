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
Usage:
  todo [-h|-v|-a]
  todo clear
  todo name [<new_name>]
  todo search <str>
  todo gist_id [<new_gist_id>]
  todo push
  todo pull [<name>]
  todo (<id> [done|undone|remove])|<task>...

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
  Remove a task                 todo 1 remove
  Rename the todo               todo name <a-new-name>
  Get the name of todo          todo name
  Push to gist.github.com       todo push
  Pull todo from gist           todo pull my_todo
  Set gist's id                 todo gist_id xxxxx
  Get gist's id                 todo gist_id
You can edit the todo.txt directly.

To feedback, please visit https://github.com/secreek/todo

"""

__version__ = '0.3.0'

from models import Task
from models import Todo

from parser import parser
from generator import generator

from utils import log
from utils import colored
from utils import ask_input

import os
from docopt import docopt


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

    def ls_tasks(self, header=True, filter=lambda task: 1):
        """ls tasks by filter. The filter's default: lambda task:1"""

        tasks = self.todo.tasks

        wrapped_name = self.wrap_todo_name(underline=True)

        if header and wrapped_name:
            print wrapped_name

        for index, task in enumerate(tasks, 1):
            if filter(task):
                print self.wrap_task(task, index)

    def print_todo_name(self):
        """print todo's name to screen"""
        name = self.wrap_todo_name()
        if name:
            print name

    @generate_to_txt
    def set_todo_name(self, new_name):
        """set todo's name a new one"""
        self.todo.name = new_name

    def get_task_by_id(self, index):
        """return task object by its index, if not found, fatal error."""
        index -= 1
        tasks = self.todo.tasks
        if index >= len(tasks):
            log.error("Task not found.")
        return tasks[index]

    def print_task(self, index):
        """Print wrapped task to term by its id"""
        task = self.get_task_by_id(index)
        print self.wrap_task(task, index)

    @generate_to_txt
    def check_task(self, index, is_done=True):
        """check a task to done or undone"""
        task = self.get_task_by_id(index)
        task.done = True if is_done else False

    @generate_to_txt
    def remove_task(self, index):
        """remove a task from list"""
        task = self.get_task_by_id(index)
        self.todo.tasks.remove(task)

    @generate_to_txt
    def add_task(self, content):
        """add a new task"""
        self.todo.tasks.append(Task(content))

    @generate_to_txt
    def clear_tasks(self):
        """clear all tasks"""
        self.tasks = []

    def run(self):

        args = docopt(__doc__, version="todo version: " + __version__)

        if args["clear"]:
            self.clear_tasks()
        elif args["name"]:
            if args["<new_name>"]:
                self.set_todo_name(args["<new_name>"])
            else:
                self.print_todo_name()
        elif args["search"]:
            self.ls_tasks(
                header=False, filter=lambda task: args["<str>"] in task.content
            )
        elif args["<id>"]:
            try:
                task_id = int(args["<id>"])
            except ValueError:
                # not an integer, add as a task
                self.add_task(args["<id>"])
                exit()
            else:
                if args["done"]:
                    self.check_task(task_id, True)
                elif args["undone"]:
                    self.check_task(task_id, False)
                elif args["remove"]:
                    self.remove_task(task_id)
                else:
                    self.print_task(task_id)
        elif args["<task>"]:
            self.add_task(" ".join(args["<task>"]))
        elif args["--all"]:
            self.ls_tasks()
        else:
            self.ls_tasks(filter=lambda task: not task.done)


def main():
    App().run()


if __name__ == '__main__':
    main()
