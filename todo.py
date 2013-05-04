#!/usr/bin/env python
# coding=utf8

__version__ = '0.1.1'


import re


class TodoSyntaxError(SyntaxError):
    pass

done = True
undone = False


class Task(object):
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
    pattern = re.compile(
        r'\s*#(?P<id>\d+)\s+(?P<content>(.(?!\(done\)))*[\S])\s+(?P<status>\(done\))?'
    )

    def __init__(self):
        pass

    def parse(self, string):
        """
        Parse single line string to dict.

        The result dict include these keys
          id            the id of the task              int
          content       the content of this task        str
          status        if the task done                done|undone
        """

        m = self.pattern.match(string)
        if not m:
            raise TodoSyntaxError
        else:
            id = int(m.group("id"))
            content = m.group("content")
            status = done if m.group("status") == "(done)" else undone
            return dict(id=id, content=content, status=status)


    def parse_lines(self, string):
        """
        Parse multiple lines, return list of dicts
        """
        dcts = []
        lines = string.splitlines()

        for line_no, line in enumerate(lines):
            if not line and line.isspace():
                # skip empty line
                continue
            else:
                try:
                    dct = self.parse(line)
                except TodoSyntaxError:
                    # skip one line's syntax error
                    # TODO: add logging info
                    print "SyntaxError at line " + str(line_no)
                else:
                    dcts.append(dct)
        return dcts

####test
s = open("todo.txt").read()
parser = Parser()
print parser.parse_lines(s)
