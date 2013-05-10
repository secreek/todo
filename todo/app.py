# coding=utf8

"""
Usage:
  todo [-h|-v|-a]
  todo push
  todo pull
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
  Push to gist.github.com       todo push
"""

__version__ = "0.1.4"

from models import Task
from models import Todo
from models import TaskNotFound
from models import Github
from parser import parser
from generator import generator
from utils import log
from utils import ask_input

import requests
from os import mkdir
from os.path import join
from os.path import exists
from os.path import expanduser
from termcolor import colored
from docopt import docopt


home = expanduser("~")  # "/home/username/"


class TodoTxt(object):
    """
    Object to manage todo.txt.

    attributes
      filepath      str     todo.txt's filepath

    methods
      read          read content from todo.txt and return todo object
      write         generate string from todo object and write it to todo.txt
    """

    def __init__(self):
        """
        Use './todo.txt' prior to '~/todo.txt' for persistent storage.
        """

        fn = "todo.txt"

        if exists(fn):
            self.filepath = fn
        else:
            home_todo_txt = join(home, fn)
            open(home_todo_txt, "a").close()  # touch it if not exists
            self.filepath = home_todo_txt

    def read(self):
        """
        Read todo.txt's content and return a dict contains todo object and file's content.

        return
          dict      e.g. {"todo": <Todo object>, "content": <str>}
        """

        content = open(self.filepath).read()

        dct = {
            "todo": parser.parse(content),
            "content": content
        }
        return dct

    def write(self, todo):
        """
        Generate todo object to string and write the string to file.
        """
        content = generator.generate(todo)
        return open(self.filepath, "w").write(content)


class Gist(object):
    """
    Parent class for GistId and GithubToken

    attributes
      todo_dir      str     the path for directory ".todo", like "/home/user/.todo"
      content       str     the content of file "~/.todo/gist_id" or "~/.todo/token"
      path          str     the path for this file ('.todo/gist_id' or '.todo/token')

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

    def save(self):
        """
        save the file's content.
        """
        return open(self.path, "w").write(self.content.strip())

    def set(self, content):
        """
        set the file's content a new value
        """
        self.content = content

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
        self.path = join(self.todo_dir, "token")

    def get(self):
        """
        call this method to get a token::
          token = GithubToken().get()

        what the get() does:
          1) read from "~/.todo/token"
          2) check if the token read is empty.
             (yes)-> 1) if empty, ask user for username and password to access api.github.com
                      2) fetch the token, set to this instance and store it.
          3) return the token (a string)
        """
        self.read()
        if self.is_empty:
            user = ask_input.text("Github user:")
            password = ask_input.password("Password for %s:" % user)
            # authorize user to github.com
            log.info("Authorize to github.com..")
            response_token = Github().authorize(user, password)

            if response_token:
                # response 200(ok)
                self.set(response_token)
                self.save()
                log.ok("Authorized success.")
                log.info("Access_token stored in %s" % self.path)
            else:
                log.error("Failed to authorize.status_code")
        return self.content


class GistId(Gist):
    """
    Gist id object.

    attributes
      path      str     the path of ".todo/gist_id" in the os

    methods
      get           get a gist_id anyway.
    """

    def __init__(self):
        super(GistId, self).__init__()
        self.path = join(self.todo_dir, "gist_id")

    def get(self):
        """
        call this method to get a gist_id::
            gist_id = GistId().get()
        what the get() dose:
          1) read the gist_id from file "~/.todo/gist_id"
          2) check if the gist_id if empty
             (yes)-> 1) if the gist_id is empty, ask user to input it.
                     2) set the instance's content as the gist_id and save it to disk.
          3) return the gist_id
        """
        self.read()
        if self.is_empty:
            self.set(ask_input.text("Gist id:"))
            self.save()
            log.ok("Gist id stored in %s" % self.path)
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
        dct = self.todo_txt.read()
        self.todo = dct["todo"]
        self.txt_content = dct["content"]

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

    def internet_error_handle(func):
        """
        This decorator checks internet error.
        """
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except requests.exceptions.ConnectionError:
                log.error("internet connection error.")
            except requests.exceptions.HTTPError:
                log.error("invalid HTTP response")
            except requests.exceptions.Timeout:
                log.error("time out.")
            except requests.exceptions.TooManyRedirects:
                log.error("too many redirects")
            except Exception, e:
                raise e
        return wrapper

    @internet_error_handle
    def push(self):
        """
        Push todo to gist.github.com
        """
        github = Github()
        gist_id = GistId().get()
        token = GithubToken().get()
        # set sessin with token

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

        log.info("Pushing %s to https://gist.github.com/%s .." % (name, gist_id))
        edit_ok = github.edit_gist(gist_id, files=files)

        if edit_ok:
            log.ok("Pushed to file '" + name + "' at https://gist.github.com/" + gist_id)
        else:
            log.error("Pushed failed.")

    @internet_error_handle
    def pull(self, name=None):
        """
        Pull todo from remote gist server.
        """

        if not name:  # if not name figured out
            name = self.todo.name  # use the todo.txt's name

        github = Github()
        gist_id = GistId().get()

        dct = github.get_gist(gist_id)

        if not dct:
            log.error("Failed to pull gist.")

        if name not in dct["files"]:
            log.error("File " + name + "not in gist: " + gist_id )

        url = dct["files"][name]["raw_url"]

        response = requests.get(url)

        if response.status_code == 200:
            print response.text
        else:
            log.error("Failed to pull file from url " + url)


    def run(self):
        """
        Get arguments from cli and run!
        """
        args = docopt(__doc__, version="todo version: " + __version__)

        if args["clear"]:
            self.clear_tasks()
        elif args["push"]:
            self.push()
        elif args["pull"]:
            self.pull()
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
