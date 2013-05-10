from setuptools import setup

setup(
    name="todo",
    version="0.2.1",
    author="hit9",
    author_email="nz2324@126.com",
    description="""
    Cli todo tool with readable storage.
    """,
    license="MIT",
    keywords="todo readable commandline cli",
    url='https://github.com/secreek/todo',
    packages=['todo'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'todo = todo.app:main'
        ]
    },
    long_description=open('README.md').read(),
    install_requires=open("requirements.txt").read().splitlines()
)
