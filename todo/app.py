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
  Search a task by content      todo search 'some str'
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

__version__ = '0.3.1'

from models import Task
from models import Todo
from models import Github

from parser import parser
from generator import generator

from utils import log
from utils import colored
from utils import ask_input

import os
import sys
import requests
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
            open(home_path, "a").close()
            path = home_path

        super(TodoTxt, self).__init__(path)


class Gist(File):
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
        self.todo_dir = os.path.join(self.home, ".todo")
        # mkdir ~/.todo if not exists
        if not os.path.exists(self.todo_dir):
            os.mkdir(self.todo_dir)
        self.content = None
        super(Gist, self).__init__(None)

    def read(self):
        """
        return file's content
        """
        if os.path.exists(self.path):
            self.content = super(Gist, self).read()
            return self.content
        return None

    def save(self, content):
        """
        save the content to file
        """
        self.content = content
        super(Gist, self).write(self.content)
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
        self.path = os.path.join(self.todo_dir, self.name)
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
                log.error("Authorization failed. %d" % response.status_code)
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
        self.path = os.path.join(self.todo_dir, self.name)
        self.read()  # must read after know his path

    def get(self, answer=None):  # add answer to figure which approach to go
        """
        call this method to get a gist_id::
            gist_id = GistId().get()
        what the get() dose:
          1) read the gist_id from file "~/.todo/gist_id"
          2) check if the gist_id if empty
             (yes)-> 1) if the gist_id is empty, ask user to input it or
                     new a gist directly.
                     2) save the new gist_id
          3) return the gist_id
        """

        if self.is_empty:
            print "Tell me the gist's id you want to push to:"
            print " 1. New a gist right now."
            print " 2. Let me input a gist's id."
            if answer is None:
                answer = ask_input.text("Input your answer(1/2):")
            if answer == '2':
                self.save(ask_input.text("Gist id:"))
            elif answer == '1':
                # new a gist
                todo_content = TodoTxt().read()
                todo = parser.parse(todo_content)
                if not todo.name:
                    name = "Todo"
                else:
                    name = todo.name

                files = {
                    name: {
                        "content": todo_content
                    }
                }

                resp = None

                github = Github()
                token = GithubToken().get()
                github.login(token)  # need to login
                log.info("Create a new gist..")
                resp = github.create_gist(files=files, description="Todo")

                if resp.status_code == 201:
                    dct = resp.json()
                    html_url = dct["html_url"].encode("utf8")
                    log.ok("Create success:%s ,"
                           "pushed at file '%s'" % (html_url, name))
                    self.save(dct["id"])
                    sys.exit()
                elif resp.status_code == 401:
                    log.warning("Github access denied, empty the old token")
                    GithubToken().save('')  # empty the token!
                    # and re create
                    self.get(answer='1')
                else:
                    log.error("Create gist failed. %d" % resp.status_code)
            else:  # exit if else input
                log.error("Invalid answer.")
        return self.content


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
        """wrap todo's name"""
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
        self.todo.tasks = []

    def push(self):
        """Push todo to gist.github.com"""
        github = Github()
        gist_id = GistId().get()
        token = GithubToken().get()

        github.login(token)

        if not self.todo.name:
            name = "Todo"
        else:
            name = self.todo.name

        files = {
            name: {
                "content": self.todo_content
            }
        }

        log.info(
            "Pushing '%s' to https://gist.github.com/%s .." % (name, gist_id)
        )
        response = github.edit_gist(gist_id, files=files)

        if response.status_code == 200:
            log.ok("Pushed success.")
        elif response.status_code == 401:
            log.warning("Github token out of date, empty the old token")
            GithubToken().save('')  # empty the token!
            self.push()  # and repush
        else:
            log.error("Pushed failed. %d" % response.status_code)

    def pull(self, name=None):
        """Pull todo from remote gist server"""

        if not name:  # if not name figured out
            if self.todo.name:
                name = self.todo.name  # use the todo.txt's name
            else:
                log.error("Please tell me todo's name to pull.")

        github = Github()
        gist_id = GistId().get()

        resp = github.get_gist(gist_id)

        if resp.status_code != 200:
            log.error("Pull failed.%d" % resp.status_code)

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
        """set gist_id"""
        gist_id = GistId()
        gist_id.save(new_gist_id.strip())

    def get_gist_id(self):
        """print gist_id to user"""
        gist_id = GistId()

        if not gist_id.is_empty:
            print gist_id.content

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
            except ValueError:
                # not an integer, add as a task
                self.add_task(args["<id>"])
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
