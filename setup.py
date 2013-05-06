from setuptools import setup

setup(
    name="todo.py",
    version="0.1.1",
    author="hit9",
    author_email="nz2324@126.com",
    description=(
        """Command Todo tool with sweet usage , readable storage format."""
    ),
    license="BSD",
    url="https://github.com/hit9/todo.py",
    install_requires = open("requirements.txt").read().splitlines(),
    scripts=['todo.py']
)
