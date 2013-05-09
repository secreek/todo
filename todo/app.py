# coding=utf8

"""
Usage:
  todo [-h|-v|-a]
  todo push
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

__version__ = "0.1.4"

from models import Task
from models import Todo
from models import TaskNotFound
from models import Github
from parser import parser
from generator import generator

from os import mkdir
from os.path import join
from os.path import exists
from os.path import expanduser
from termcolor import colored
from docopt import docopt
from getpass import getpass


home = expanduser("~")  # home path "~" => "/home/username/"


class TodoTxt(object):
    """
    Use './todo.txt' prior to '~/todo.txt' for persistent storage.
    """

    def __init__(self):
        fn = "todo.txt"

        if exists(fn):
            self.filepath = fn
        else:
            home_todo_txt = join(home, fn)
            open(home_todo_txt, "a").close()  # touch it if not exists
            self.filepath = home_todo_txt

    def read(self):
        """
        Return todo object.
        """
        content = open(self.filepath).read()
        return parser.parse(content)

    def write(self, todo):
        """
        Write todo object to file.
        """
        content = generator.generate(todo)
        open(self.filepath, "w").write(content)


class Gist(object):

    def __init__(self):
        """
        mkdir ~/.todo if not exists
        """
        self.todo_dir = join(home, ".todo")
        self.content = None
        if not exists(self.todo_dir):
            mkdir(self.todo_dir)

    def read(self):
        if exists(self.path):
            self.content = open(self.path).read().strip()
            return self.content
        return None

    def save(self):
        return open(self.path, "w").write(self.content.strip())


class GithubToken(Gist):

    def __init__(self):
        super(GithubToken, self).__init__()
        self.path = join(self.todo_dir, "token")
        self.read()


class GistId(Gist):

    def __init__(self):
        super(GistId, self).__init__()
        self.path = join(self.todo_dir, "gist_id")
        self.read()


class App(object):
    """
    Todo command line application.

    ::
        app = App()
        app.run()
    """
    def __init__(self):
        self.todo_txt = TodoTxt()
        self.todo = self.todo_txt.read()

    def write_to_txt(func):
        """
        Decorator, write to todo.txt after func
        """
        def __decorator(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.todo_txt.write(self.todo)
        return __decorator

    def print_task(self, task):
        """
        Print single task to terminal.
        """
        if task.done:
            state = colored("✓", "green")
        else:
            state = colored("✖", "red")
        content = colored(task.content, "blue")
        task_id = colored(str(task.id))
        print task_id + "." + " " + state + "  " + content

    def print_task_by_id(self, task_id):
        """
        Pringt single task by its id.
        """
        self.print_task(self.todo.get_task(task_id))

    def print_todo_name(self):
        """
        Print todo's name
        """
        name = generator.gen_name(self.todo.name)
        if name:
            print colored(name, "cyan")

    def with_todo_name(func):
        """
        Decorator, print todo's name before func()
        """
        def __decorator(self, *args, **kwargs):
            self.print_todo_name()
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

    @write_to_txt
    def check_task(self, task_id):
        """
        check one task to done.
        """
        task = self.todo.get_task(task_id)
        task.done = True

    @write_to_txt
    def undo_task(self, task_id):
        """
        check one task to undone.
        """
        task = self.todo.get_task(task_id)
        task.done = False

    @write_to_txt
    def clear_tasks(self):
        """
        Clear all tasks.
        """
        self.todo.clear()

    @write_to_txt
    def add_task(self, content):
        """
        Add a new task
        """
        self.todo.new_task(content)

    @write_to_txt
    def remove_task(self, task_id):
        """
        Remove task from list
        """
        self.todo.remove_task(task_id)

    def push(self):
        """
        Push todo to gist.github.com
        """
        github = Github()
        gist_id = GistId()
        token = GithubToken()

        if not gist_id.content:
            gist_id.content = raw_input("Gist id:")
            gist_id.save()
        if not token.content:
            user = raw_input("Github user:")
            password = getpass("Password for %s:" % user)
            gh_token = github.authorize(user, password)
            if gh_token:
                token.content = gh_token
                token.save()
            else:
                exit("Failed to login.")
        github.login(token.content)

        if not self.todo.name:
            name = "NoName"
        else:
            name = self.todo.name
        files = {
            name: {
                "content": generator.generate(self.todo)
            }
        }

        is_ok = github.edit_gist(gist_id.content, files=files)

        if is_ok:
            print "Pushed to file '" + name + "' at https://gist.github.com/" + gist_id.content
        else:
            print "Pushed failed."

    def run(self):
        """
        Get arguments from cli and run!
        """
        args = docopt(__doc__, version="todo version: " + __version__)

        if args["clear"]:
            self.clear_tasks()
        if args["push"]:
            self.push()
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
    Run app.
    """
    App().run()

if __name__ == '__main__':
    main()
