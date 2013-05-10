# coding=utf8

"""
Utils used in cli app.
"""

from getpass import getpass


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


ask_input = AskInput()  # build ask_input for loop asks..
