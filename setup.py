from __future__ import absolute_import
from __future__ import unicode_literals
from setuptools import setup, find_packages
import ast
import re

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('umakaviewer/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="umakaviewer",
    version=version,
    url="https://github.com/dbcls/umakaviewer",
    author="DBCLS",
    author_email="fumiya.kubota@glucose.jp",
    maintainer='fumiya-kubota',
    maintainer_email='fumiya.kubota@glucose.jp',
    description="",
    long_description="",
    packages=find_packages(),
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      umakaparser = umakaviewer.services:cmd
    """,

)
