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
  Models in this application, Task and Todo,
see theirs docs for help.
"""


class Task(object):
    """
      A task looks like::

          - [x] Go shopping

      Use '[x]' to mark a task done.

      attributes
        content   str  (required)
        done      bool (optional, default: False)
    """

    def __init__(self, content, done=False):
        self.content = content
        self.done = done


class Todo(object):
    """
      A todo is made up of tasks.

      attributes
        name    str     (optional, default: '')todo's name, should be unique
      in all your todos in your os.
        tasks   list    (optional, default: [])tasks in this todo, each of
      them is an instance of Task
    """

    def __init__(self, name=None, tasks=None):
        self.name = '' if name is None else name
        self.tasks = [] if tasks is None else tasks
