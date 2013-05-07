from setuptools import setup

setup(
    name="todo",
    version="0.1.1",
    author="hit9",
    author_email="nz2324@126.com",
    description="Command Todo tool with sweet usage , readable storage format",
    license="MIT",
    keywords="todo readable commandline cli",
    url='http://github.com/hit9/todo',
    packages=['todo'],
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'todo = todo.script:main'
        ]
    },
    install_requires = open("requirements.txt").read().splitlines()
)
