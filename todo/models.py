# coding=utf8

import json
import requests


class Task(object):
    """
    A task looks like

      1. [x]  Go shopping

    if this task has been done, use '[x]' to mark it.
    else, leave there blank.

    Attributes
      id        int
      content   str
      done      bool
    """

    def __init__(self, task_id, content, done=False):
        self.id = task_id
        self.content = content
        self.done = done


class TaskNotFound(Exception):
    """
    If the asked task not found in given todo, this error will be raised
    """
    pass


class Todo(object):
    """
    A todo is made up of tasks.

    Attributes
      name    str     todo's name, should be unique in all your todos in your os.
      tasks   list    tasks in this todo, each of them is an instance of Task
    """

    def __init__(self, name=None, tasks=[]):
        # We set default value of argument 'name' as None,
        # because the name is optional
        self.name = name
        self.tasks = tasks

    def next_id(self):
        """
        Generate the next id should be.

        For the id of one task is an integer, the id(s) of a todo object will be made up of
        many integers. We find the max of them, and plus one to it as the next id for new task
        """

        ids = [task.id for task in self.tasks]
        max_id = max(ids) if ids else 0  # method `max` broken with empty list
        return (max_id + 1)

    def new_task(self, content, done=False):
        """
        Append a new task to todo.

        parameters:
          content       the content of task
          done          if the task done(default: False)
        """
        task = Task(self.next_id(), content, done)
        return self.tasks.append(task)

    def get_task(self, task_id):
        """
        Get task by its id
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        # Not found
        raise TaskNotFound

    def remove_task(self, task_id):
        """
        Remove task by its id
        """
        task = self.get_task(task_id)
        return self.tasks.remove(task)

    def clear(self):
        """
        Clear tasks list!
        """
        self.tasks = []


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

    client_id = "164f614c7c92c7a8c6bd"
    client_secret = "d37ce92277ac9c2e6b90c81039f068ea9bb765c2"
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
        if success, return token(a string). else return None
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
        r = self.session.post("https://api.github.com/authorizations", data=data_json, headers=headers)
        if r.status_code == 201:
            token = r.json()["token"]
            return token
        else:
            return None

    def login(self, token):
        """
        Login to github with token
        """
        self.session.headers.update({'Authorization': 'token ' + token})

    def edit_gist(self, gist_id, files={}, description=""):
        """
        Edit a gist, require auth.
        If edit successfully, return True, else False

        parameters
          gist_id       str      gist's id
          files         dict     {file_name:{"content":"xxxx", "filename":"xxxxx"}}
          description   str      gist's description

        return boolen
        """
        data = dict(
            files=files,
            description=description
        )
        response = self.session.patch("https://api.github.com/gists/" + gist_id, data=json.dumps(data))
        return response.status_code == 200

    def get_gist(self, gist_id):
        """
        Fetch a single gist down, return dict.

        To get some certain file's raw_url::
            return["files"]["filename"]["raw_url"]

        To fetch content of gist's file::
           r = requests.get(file_raw_url)
           print r.text
        """
        re = self.session.get("https://api.github.com/gists/" + gist_id)
        if re.status_code == requests.codes.ok:
            return re.json()
        return None
