from __future__ import unicode_literals
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "mixmaster",
    version = "1.0.1",
    author = "Bryan W Weber",
    author_email = "bryan.w.weber@gmail.com",
    description = "The GUI for Cantera 2.4",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Cantera/mixmaster",
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)