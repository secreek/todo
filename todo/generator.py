# coding=utf8

"""
Generator from todo object to todo format string
"""

from models import Task
from models import Todo


class Generator(object):
    """
    Generator from todo object to readable string.
    """

    newline = "\n"

    def gen_task_id(self, task_id):
        """
        int => str      e.g.  12 => '12.'
        """
        return str(task_id) + "."

    def gen_task_done(self, done):
        """
        boolen => str   e.g.  True => '[x]'
        """
        if done is True:
            return '[x]'
        else:
            return '   '

    def gen_task_content(self, content):
        """
        str => str
        """
        return content

    def gen_name(self, name):
        """
        str => str      e.g.  'name' => 'name\n------'
        """
        if name:
            return name + self.newline +  '-' * len(name)

    def gen_task(self, task):
        """
        Task => str
        e.g.    Task(1, "Write email", True) => '1. [x]  Write email'
        """
        lst = []
        lst.append(self.gen_task_id(task.id))
        lst.append(self.gen_task_done(task.done))
        lst.append(self.gen_task_content(task.content))
        return " ".join(lst)

    def generate(self, todo):
        """
        Generate todo object to string.

        e.g.  Todo(name, tasks) => "1. (x) do something..."
        """
        lst = []

        head = self.gen_name(todo.name)

        if head:
            lst.append(head)

        for task in todo.tasks:
            lst.append(self.gen_task(task))

        return self.newline.join(lst)


generator = Generator()  # build generator
