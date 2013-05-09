# coding=utf8

"""
Usage:
  todo [-h|-v|-a]
  todo clear
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
"""

__version__ = "0.1.3"

from models import Task
from models import Todo
from models import TaskNotFound
from parser import parser
from generator import generator

from os.path import join
from os.path import exists
from os.path import expanduser
from termcolor import colored
from docopt import docopt


class App(object):
    """
    Todo cli application.

    ::
        app = App()
        app.run()
    """

    def __init__(self):
        self.todo = self.read()

    @property
    def todo_txt(self):
        """
        Use './todo.txt' prior to '~/todo.txt' for persistent storage.
        """
        fn = 'todo.txt'
        home_fn = join(expanduser("~"), fn)
        open(home_fn, "a").close()  # touch if not exists

        if exists(fn):
            return fn
        else:
            return home_fn

    def read(self):
        """
        Read from todo.txt, return todo object.
        """
        content = open(self.todo_txt).read()
        return parser.parse(content)

    def write(self):
        """
        Write this todo to todo.txt
        """
        content = generator.generate(self.todo)
        open(self.todo_txt, "w").write(content)

    def sync_to_txt(func):
        """
        Decorator, write to todo.txt after func()
        """
        def __decorator(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.write()
        return __decorator

    def print_task(self, task):
        """
        Print single task to terminal.
        """
        if task.done:
            state = colored('✓', 'green')
        else:
            state = colored('✖', 'red')
        content = colored(task.content, "blue")
        task_id = colored(str(task.id), "cyan")
        print task_id + '.' + ' ' + state + '  ' + content

    def print_task_by_id(self, task_id):
        """
        Pringt single task by its id.
        """
        self.print_task(self.todo.get_task(task_id))

    def print_name(self):
        """
        Print todo's name to terminal.
        """
        name = generator.gen_name(self.todo.name)
        print colored(name, "cyan")

    def with_todo_name(func):
        """
        Print name to screen at first.
        """
        def __decorator(self, *args, **kwargs):
            self.print_name()
            return func(self, *args, **kwargs)
        return __decorator

    @with_todo_name
    def ls_tasks(self):
        """
        ls all tasks output to screen
        """
        for task in self.todo.tasks:
            self.print_task(task)

    @with_todo_name
    def ls_undone_tasks(self):
        """
        ls all undone tasks.
        """
        for task in self.todo.tasks:
            if not task.done:
                self.print_task(task)

    @sync_to_txt
    def check_task(self, task_id):
        """
        check one task to done.
        """
        task = self.todo.get_task(task_id)
        task.done = True

    @sync_to_txt
    def undo_task(self, task_id):
        """
        check one task to undone.
        """
        task = self.todo.get_task(task_id)
        task.done = False

    @sync_to_txt
    def clear_tasks(self):
        """
        Clear all tasks.
        """
        self.todo.clear()

    @sync_to_txt
    def add_task(self, content):
        """
        Add a new task
        """
        self.todo.new_task(content)

    @sync_to_txt
    def remove_task(self, task_id):
        """
        Remove task from list
        """
        self.todo.remove_task(task_id)

    def run(self):
        """
        Get arguments from cli and run!
        """

        args = docopt(__doc__, version="todo version: " + __version__)

        if args["clear"]:
            self.clear_tasks()
        elif args["<id>"]:
            try:
                task_id = int(args["<id>"])
                if args["done"]:
                    self.check_task(task_id)
                elif args["undone"]:
                    self.undo_task(task_id)
                elif args["remove"]:
                    self.remove_task(task_id)
                else:
                    self.print_task_by_id(task_id)
            except ValueError:
                # if not an integer format str, use as a task
                self.add_task(args["<id>"])
            except TaskNotFound:
                print colored("No task at id '" + str(task_id) + "'.", "red")
        elif args["<task>"]:
            self.add_task(" ".join(args["<task>"]))
        elif args["--all"]:
            self.ls_tasks()
        else:
            self.ls_undone_tasks()


def main():
    """
    Run todo in cli
    """
    app = App()
    app.run()

if __name__ == '__main__':
    main()
