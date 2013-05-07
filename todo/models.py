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

    def __init__(self, _id, content, done=False):
        self.id = _id
        self.content = content
        self.done = done


class TaskNotFound(Exception):
    pass


class Todo(list):
    """
    A todo is kind of a list of tasks.
    """

    def __getitem__(self, task_id):
        """
        Get task by id.
        """
        for task in self:
            if task.id == task_id:
                return task
        raise TaskNotFound

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

    def remove_task(self, task_id):
        """
        Remove a task by id
        """
        self.remove(self[task_id])

    def check_task(self, task_id):
        """
        Check task's status to done
        """
        self[task_id].done = True

    def undo_task(self, task_id):
        """
        Undone some task
        """
        self[task_id].done = False

    def clear(self):
        """
        Clear all tasks!
        """
        self[:] = []
