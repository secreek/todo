# coding=utf8


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
        return  (max_id + 1)

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
