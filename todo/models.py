# coding=utf8


class Task(object):
    """
    One task looks like

      1. (x) Go shopping

    if this task not done, leave there blank.

    Attrributes
      id        int
      content   str
      done      bool
    """

    def __init__(self, id, content, done=False):
        self.id = id
        self.content = content
        self.done = done


class TaskNotFound(Exception):
    pass


class Todo(list):
    """
    A todo is kind of a list of tasks.
    But todo[task_id] will get an item which id is task_id
    """

    def next_id(self):
        """
        Return next id should be.
        """
        ids = [task.id for task in self]
        max_id = max(ids) if ids else 0
        return (max_id + 1)

    def new_task(self, content):
        """
        Append a new undone task to todo
        """
        task = Task(self.next_id(), content, False)
        return self.append(task)

    def __getitem__(self, id):
        """
        Get task by id.
        """
        for task in self:
            if task.id == id:
                return task
        raise TaskNotFound

    def check_task(self, id):
        """
        Check task's status to done
        """
        self[id].done = True

    def undo_task(self, id):
        """
        Undone some task
        """
        self[id].done = False

    def clear(self):
        """
        Clear all tasks!
        """
        self[:] = []
