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

import json
import requests


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


class Github(object):
    """
    Github object to auth user, edit gist .etc

    e.g. ::
        gh = Github()
        gh.login(token='xxxx')
        gh.edit_gist()

    And about the authorize::
        gh = Github()
        token = gh.authorize(login, password)  # authorize itself and login
        gh.login(token=token)
        gh.edit_gist()  # do things..
    """

    # The client_secret should not be shared in principle.
    # Otherwise a proxy script running all days around will be needed.
    # DONT DO THINGS STUPID.
    # The client_secret can be reset. Also, this application matsers nothing.
    # Thanks.

    client_id = "141eec25d89ad52c380b"
    client_secret = "5bf0c8d82a753e4efbdf045400989f8fa93843d8"
    note_url = "https://github.com/secreek/todo"
    note = "Cli todo tool with readable storage."
    scopes = ["user", "gist"]

    def __init__(self):
        """
          Init an instance of Github. New an empty session.
        """
        self.session = requests.Session()  # init a session

    def authorize(self, login, password):
        """
          Fetch access_token from github.com using username & password.
          return the response object
        """
        self.session.auth = (login, password)
        data = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            note=self.note,
            note_url=self.note_url,
            scopes=self.scopes
        )

        data_json = json.dumps(data)
        headers = {'content-type': 'application/json'}
        return self.session.post("https://api.github.com/authorizations", data=data_json, headers=headers)

    def login(self, token):
        """
          Login to github with token
        """
        self.session.headers.update({'Authorization': 'token ' + token})

    def edit_gist(self, gist_id, files={}, description=""):
        """
          Edit a gist, require auth.

          parameters
            gist_id       str      gist's id
            files         dict     {file_name:{"content":"xxxx", "filename":"xxxxx"}}
            description   str      gist's description

          return response
        """
        data = dict(
            files=files,
            description=description
        )
        response = self.session.patch("https://api.github.com/gists/" + gist_id, data=json.dumps(data))
        return response

    def get_gist(self, gist_id):
        """
          Fetch a single gist down, return response.

          ::
              resp = get_gist("xxx")
              dct = resp.json()

          To get some certain file's raw_url::
              dct["files"]["filename"]["raw_url"]

          To fetch content of gist's file::
             r = requests.get(file_raw_url)
             print r.text
        """
        return self.session.get("https://api.github.com/gists/" + gist_id)

    def create_gist(self, files, public=False, description=""):
        """
          Create a new gist.

          ::
              create_gist(files, public=False, description="xxxx")  # return response

          The files is a dict, {filename: {"content": content}}

          201 code for success created.

        """
        data = dict(
            files=files,
            public=public,
            description=description
        )

        response = self.session.post("https://api.github.com/gists", data=json.dumps(data))

        return response
