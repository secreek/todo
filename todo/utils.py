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

"""Utils used in cli app"""

import sys
from getpass import getpass


class Color(object):
    """Util to print 256 color(xterm-256)"""

    # common colors
    colors = {
        'red': 160,
        'green': 35,
        'yellow': 136,
        'blue': 33,
        'magenta': 35,
        'cyan': 37,
        'white': 231,
        'violet': 61,
        'orange': 166,
        'gray': 245,
    }

    prefix = '\x1b[38;5;'

    suffix = '\x1b[0m'

    def colored(self, string, color=None):
        """
          ::
              colored("string", "red")  # return str
        """
        if color not in self.colors:
            color = 'white'
        value = self.colors[color]
        return (self.prefix + '%dm%s' + self.suffix) % (value, string)

colored = Color().colored


class AskInput(object):
    """Ask user to input text or password"""

    def text(self, message):
        """Ask user to input text"""
        i = ''
        while not i:
            i = raw_input(message)
        return i

    def password(self, message):
        """Ask user to input password without echo back"""
        passwd = ''
        while not passwd:
            passwd = getpass(message)
        return passwd


ask_input = AskInput()  # build ask_input for loop asks..


class Log(object):
    """logging messages to terminal"""

    def error(self, message):
        """Print red error message and kill the script"""
        print colored("[error]\t" + message, "red")
        sys.exit(1)

    def info(self, message):
        """Print info"""
        print "[info]\t" + message

    def ok(self, message):
        """Tell the user the success message"""
        print colored("[ok]\t" + message, "green")

    def warning(self, message):
        """Warning message"""
        print colored("[warn]\t" + message, "yellow")


log = Log()
