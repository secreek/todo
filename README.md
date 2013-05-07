todo
----

Cli todo tool with readable storage.

![screen-shot](screen-shot.png)

Install
-------

Use pip install from git

    [sudo] pip install git+git://github.com/secreek/todo.git

Usage
------

```
Usage:
  test.py [-h|-v|-a]
  test.py clear
  test.py (<id> [done|undone|remove])|<task>...

Options:
  -h --help      show this message
  -v --version   show version
  -a --all       show all

Examples:
  Add a task                    todo Go shopping!
  Check a task as done          todo 1 done
  Check a task as undone        todo 1 undne
  Print all tasks               todo --all
  Print undone tasks            todo
  Remove a task                 todo 1 remove
```

Storage
-------

`todo` will use `./todo.txt` prior to `~/todo.txt` for persistent storage.

Well, the storage is readable, sample:

```
1. (x) Clean the room
2.     Go shopping.
```

Or checkout this file: [todo.txt](todo.txt)


License
--------

MIT
