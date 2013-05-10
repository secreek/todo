# coding=utf8

"""
Utils used in cli app.
"""
import sys
from getpass import getpass
from termcolor import colored


class AskInput(object):
    """
    Ask user to input.
    """
    def text(self, message):
        """
        Ask user to input text.
        """
        i = ""
        while not i:
            i = raw_input(message)
        return i

    def password(self, message):
        """
        Ask user to input password without echo back.
        """
        passwd = ""
        while not passwd:
            passwd = getpass(message)
        return passwd


class Log(object):
    """
    logging messages to terminal
    """

    def error(self, message):
        """
        Print red error message and kill the script.
        """
        print colored("[error]\t" + message, "red")
        sys.exit(1)

    def info(self, message):
        """
        Print info
        """
        print "[info]\t" + message

    def ok(self, message):
        """
        Tell the user the success message.
        """
        print colored("[ok]\t" + message, "green")

    def warning(self, message):
        """
        Warning message.
        """
        print colored("[warning]\t" + message, "yello")

ask_input = AskInput()  # build ask_input for loop asks..
log = Log()
