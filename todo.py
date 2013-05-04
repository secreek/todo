#!/usr/bin/env python
# coding=utf8

__version__ = '0.1.1'


import re


class TodoSyntaxError(object):pass  # single line syntaxerror

# marks
done = True
undone = False


class Task(object):  # one line, one task
    """
    One line, one task.

    Attributes
      content  What the task is?    string
      status   done or undone?      done or undone
    """
    def __init__(self, content, status=undone, id=None):
        self.content = content
        self.status = status
        self.id = id

    @property
    def done(self):
        return self.status is done

    @property
    def undone(self):
        return self.status is undone


class Parser(object):  # Parser for todo format string

    # pattern to match signle line todo
    pattern  = re.compile(
        r'\s*#(?P<id>\d+)\s+(?P<content>(.(?!\(done\)))*[\S])\s+(?P<status>\(done\))?'
    )

    def __init__(self):
        pass

    def parse(self, string):
        """
        Parse single line string to dict.
        The result dict include these keys
          id        the id of the task          int
          content   the content of this task    str
          status    if the task done            done or undone
        """
        m = self.pattern.match(string)
        if not m:
            return TodoSyntaxError
        else:
            id = int(m.group("id"))
            content = m.group("content")
            status = done if m.group("status") == "(done)" else undone
            return dict(id=id, content=content, status=status)


####test
s = open("todo.txt").read()

parser = Parser()

lines = s.splitlines()

for line in lines:
    print parser.parse(line)
