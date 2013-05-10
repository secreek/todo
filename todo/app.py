# coding=utf8

"""
Usage:
  todo [-h|-v|-a]
  todo clear
  todo push
  todo pull [<name>]
  todo name [<new_name>]
  todo gist_id [<new_gist_id>]
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

"""

__version__ = "0.2.0"

from models import Task
from models import Todo
from models import TaskNotFound
from models import Github
from parser import parser
from generator import generator
from utils import log
from utils import ask_input

from os import mkdir
from os.path import join
from os.path import exists
from os.path import expanduser

import requests
from termcolor import colored
from docopt import docopt

home = expanduser("~")  # "/home/username/"


class TodoTxt(object):
    """
    Object to manage todo.txt.

    attributes
      path      str     todo.txt's filepath
    """

    def __init__(self):
        """
        Use './todo.txt' prior to '~/todo.txt' for persistent storage.
        """
        fn = "todo.txt"

        if exists(fn):
            self.path = fn
        else:
            home_todo_txt = join(home, fn)
            open(home_todo_txt, "a").close()  # touch it if not exists
            self.path = home_todo_txt

    def read(self):
        """
        Read todo.txt's content.
        """

        return open(self.path).read().strip()

    def write(self, content):
        """
        Write string to todo.txt
        """
        return open(self.path, "w").write(content)


class Gist(object):
    """
    Parent class for GistId and GithubToken

    attributes
      todo_dir      str     the path of directory ".todo"
      content       str     the content of the file
      path          str     the path of the file

    methods
      read          read from file(gist_id or token) and return its content
      save          save the content to file(..)

    """

    def __init__(self):
        self.todo_dir = join(home, ".todo")
        self.content = None
        self.path = None
        # mkdir ~/.todo if not exists
        if not exists(self.todo_dir):
            mkdir(self.todo_dir)

    def read(self):
        """
        return file's content
        """
        if exists(self.path):
            self.content = open(self.path).read().strip()
            return self.content
        return None

    def save(self, content):
        """
        save the content to file
        """
        self.content = content
        open(self.path, "w").write(self.content.strip())
        log.info("%s stored in %s" % (self.name, self.path))

    @property
    def is_empty(self):
        """
        If the content is empty, return True, else False
        """
        return not self.content


class GithubToken(Gist):
    """
    Github's access_token object.

    attributes
      path          str     its filepath in the os

    methods
      get           Get a token anyway.
    """

    def __init__(self):
        super(GithubToken, self).__init__()
        self.name = "github_token"
        self.path = join(self.todo_dir, self.name)
        self.read()  # must read after know his path

    def get(self):
        """
        call this method to get a token::
          token = GithubToken().get()

        what the get() does:
          1) read from "~/.todo/token"
          2) check if the token read is empty.
             (yes)-> 1) if empty,
                        ask user for user&passwd to access api.github.com
                      2) fetch the token, set to this instance and store it.
          3) return the token (a string)
        """
        if self.is_empty:
            user = ask_input.text("Github user:")
            password = ask_input.password("Password for %s:" % user)

            log.info("Authorize to github.com..")
            response = Github().authorize(user, password)

            if response.status_code == 201:
                # 201 created
                log.ok("Authorized success.")
                # get token from dict
                token = response.json()["token"]
                self.save(token)
            else:
                log.error("Failed to authorize. status code: %s" % str(response.status_code))
        return self.content


class GistId(Gist):
    """
    Gist id object.

    attributes
      name      str
      path      str     the path of ".todo/gist_id" in the os

    methods
      get           get a gist_id anyway.
    """

    def __init__(self):
        super(GistId, self).__init__()
        self.name = "gist_id"
        self.path = join(self.todo_dir, self.name)
        self.read()  # must read after know his path

    def get(self):
        """
        call this method to get a gist_id::
            gist_id = GistId().get()
        what the get() dose:
          1) read the gist_id from file "~/.todo/gist_id"
          2) check if the gist_id if empty
             (yes)-> 1) if the gist_id is empty, ask user to input it.
                     2) save the new gist_id
          3) return the gist_id
        """

        if self.is_empty:
            self.save(ask_input.text("Gist id:"))
        return self.content


class App(object):
    """
    Todo command line application.

    ::
        app = App()
        app.run()
    """
    def __init__(self):
        self.todo_txt = TodoTxt()
        self.txt_content = self.todo_txt.read()
        self.todo = parser.parse(self.txt_content)

    def write_to_txt(func):
        """
        Decorator, write to todo.txt after func
        """
        def __decorator(self, *args, **kwargs):
            func(self, *args, **kwargs)
            content = generator.generate(self.todo)
            self.todo_txt.write(content)
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
        task_id = colored(str(task.id), "cyan")
        print task_id + "." + " " + state + "  " + content

    def print_task_by_id(self, task_id):
        """
        Pringt single task by its id.
        """
        self.print_task(self.todo.get_task(task_id))

    def print_todo_name(self):
        """
        Print todo's name, without "----"
        """
        if self.todo.name:
            print colored(self.todo.name, "cyan")

    def with_todo_name(func):
        """
        Decorator, print todo's name before func(), with "---"
        """
        def __decorator(self, *args, **kwargs):
            self.print_todo_name()
            if self.todo.name:
                print colored("-" * len(self.todo.name), "cyan")
            return func(self, *args, **kwargs)
        return __decorator

    @write_to_txt
    def set_todo_name(self, new_name):
        """
        Set todo's name
        """
        self.todo.name = new_name

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
        gist_id = GistId().get()
        token = GithubToken().get()

        github.login(token)

        if not self.todo.name:
            name = "NoName"
        else:
            name = self.todo.name

        files = {
            name: {
                "content": self.txt_content
            }
        }

        log.info(
            "Pushing '%s' to https://gist.github.com/%s .." % (name, gist_id)
        )
        response = github.edit_gist(gist_id, files=files)

        if response.status_code == 200:
            log.ok("Pushed success.")
        elif response.status_code == 401:
            log.warning("Github token is out of date")
            GithubToken().save('')  # empty the token!
            self.push()  # and repush
        else:
            log.error("Pushed failed, server responded with status code: %s" % response.status_code )

    def pull(self, name=None):
        """
        Pull todo from remote gist server.
        """

        if not name:  # if not name figured out
            if self.todo.name:
                name = self.todo.name  # use the todo.txt's name
            else:
                log.error("Please tell me todo's name to pull.")

        github = Github()
        gist_id = GistId().get()

        resp = github.get_gist(gist_id)

        if resp.status_code != 200:
            log.error("Failed to pull gist, status code: %s" % resp.status_code)

        dct = resp.json()  # get out the data

        u_name = name.decode("utf8")  # decode to unicode

        # Note that data back from github.com is unicode
        if u_name not in dct["files"]:
            log.error("File '%s' not in gist: %s" % (name, gist_id))

        u_url = dct["files"][u_name]["raw_url"]
        url = u_url.encode("utf8")

        response = requests.get(url)

        if response.status_code == 200:
            todo_content = response.text.encode("utf8")
            self.todo_txt.write(todo_content)
            log.ok("Pulled success to file '%s'" % self.todo_txt.path)
        else:
            log.error("Failed to pull file from %s" % url)

    def set_gist_id(self, new_gist_id):
        """
        set gist_id
        """
        gist_id = GistId()
        gist_id.save(new_gist_id.strip())

    def get_gist_id(self):
        """
        print gist_id to user
        """
        gist_id = GistId()

        if not gist_id.is_empty:
            print gist_id.content

    def run(self):
        """
        Get arguments from cli and run!
        """
        args = docopt(__doc__, version="todo version: " + __version__)

        if args["clear"]:
            self.clear_tasks()
        elif args["name"]:
            if args["<new_name>"]:
                self.set_todo_name(args["<new_name>"])
            else:
                self.print_todo_name()
        elif args["pull"]:
            self.pull(args["<name>"])
        elif args["push"]:
            self.push()
        elif args["gist_id"]:
            if args["<new_gist_id>"]:
                self.set_gist_id(args["<new_gist_id>"])
            else:
                self.get_gist_id()
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
                log.error("No task at id '" + str(task_id) + "'.")
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
