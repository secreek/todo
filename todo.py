#!/usr/bin/env python
# coding=utf8

__version__ = '0.1.1'


from ply import lex
from ply import yacc


class Task(object):
    """
    Task object.
    One task looks like:

      #1 Go shopping (done)

    The '#1' is id, 'Go shopping' is the content and the '(done)' is the status
    And the status is optional(default: undone).

    id          int     task's id
    content     str     task'content
    status      bool    is this task done?
    """
    def __init__(self, id, content, status=False):
        self.id = id
        self.content = content
        self.status = status

    @property
    def done(self):
        # return True if this task has been done.
        return self.status


class Tag(object):
    """
    Tag object.
    Tags split tasks list like milestones.
    One tag looks like:
      ----- The tasks above is before 12-04-05 ----
    The string 'The....05' is the tag's content, it should be unique.

    name        str     tag's name, should be unique in all tags
    """

    def __init__(self, name):
        self.name = name


class TodoLexer(object):

    tokens = (
        "ID",
        "TAG",
        "STATUS",
        "TASK",
    )

    t_ignore = "\x20\x09"  # ignore spaces and tabs

    def t_ID(self, t):
        r'\#\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
        t.value = int(t.value[1:])
        return t

    def t_TAG(self, t):
        r'-+(.*)-+'
        t.value = ''.join(i for i in t.value if i != '-')
        t.value = t.value.strip()
        return t

    def t_STATUS(self, t):
        r'(\(done\))|(\(undone\))'
        t.value = (t.value == "(done)")
        return t

    def t_TASK(self, t):
        r'(.(?!\(done\))(?!\(undone\)))*\S'
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise SyntaxError(
            "Illegal character: '%s' at Line %d" % (t.value[0], t.lineno)
        )

    def __init__(self):
        self.lexer = lex.lex(module=self)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print tok


class TodoParser(object):

    tokens = TodoLexer.tokens

    def p_error(self, p):
        if p:
            raise SyntaxError(
                "Character '%s' at line %d, \
                token: %r" % (p.value[0], p.lineno, p)
            )
        else:
            raise SyntaxError("SyntaxError at EOF")

    def p_start(self, p):
        "start : translation_unit"
        p[0] = self.lst

    def p_translation_unit(self, p):
        """
        translation_unit : translate_single_line
                         | translation_unit translate_single_line
                         |
        """
        pass

    def p_translation_task(self, p):
        """
        translate_single_line : ID TASK STATUS
                              | ID TASK
        """
        if len(p) < 4:
            status = False
        else:
            status = p[3]
        task = Task(p[1], p[2], status)
        self.lst.append(task)

    def p_translation_tag(self, p):
        """
        translate_single_line : TAG
        """
        tag = Tag(p[1])
        self.lst.append(tag)

    def __init__(self):
        self.parser = yacc.yacc(module=self, debug=0, write_tables=0)

    def parse(self, data):
        # reset list
        self.lst = list()
        return self.parser.parse(data)


lexer = TodoLexer()
parser = TodoParser()
lst = parser.parse(open("todo.txt").read())
for x in lst:
    if isinstance(x, Task):
        print x.id, x.content, x.done
    else:
        print x
