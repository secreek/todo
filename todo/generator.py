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
  Generator from <Todo instance> to string::

      generator.generate(<Todo instance>)  # return str
"""

from models import Task
from models import Todo


class Generator(object):
    """
      Generator from <Todo instance> to string.
    """

    newline = '\n'

    def generate_task(self, task):
        """
          <Task> => <str>
          e.g.::

              Task('Go shopping', True)

              =>

              '- [x] Go shopping'

        """
        done = '[x]' if task.done else '   '
        content = task.content
        return ' '.join(['-', done, content])

    def generate_todo(self, todo):
        """
          <Todo instance> => <str>
          parameters
            todo   the <Todo instance>
        """
        lines = []

        if todo.name:
            lines.append(todo.name)
            name_len = len(todo.name)
            if name_len < 3:
                num = 3
            else:
                num = name_len
            lines.append(num * '-')

        for task in todo.tasks:
            lines.append(self.generate_task(task))

        return self.newline.join(lines)

    # alias to generate_todo
    generate = generate_todo

generator = Generator()  # build generator
