# coding=utf8
"""
Generator from todo to todo format string.

  from todo.generator import generator
  generator.generate(todo)  # return str

"""
from models import Task
from models import Todo


class TodoGenerator(object):
    """
    Generator from python list to string.
    """

    g_newline = "\n"

    def g_id(self, v):
        return str(v) + "."

    def g_done(self, v):
        if v is True:
            return '(x)'
        else:
            return '   '

    def g_task(self, v):
        return v

    def gen_task(self, task):
        lst = []
        lst.append(self.g_id(task.id))
        lst.append(self.g_done(task.done))
        lst.append(self.g_task(task.content))
        return " ".join(lst)

    def generate(self, todo):
        """
        Generate todo to string format.

        e.g.
          [<task object>, ..] => "1. (x) do something .."
        """
        re = []
        for i in todo:
            if isinstance(i, Task):
                re.append(self.gen_task(i))
            else:
                raise SyntaxError('Not support type: ' + type(i))
        return self.g_newline.join(re)


generator = TodoGenerator()  # build generator
