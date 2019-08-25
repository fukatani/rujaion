#!/usr/bin/env python3
import imp
from setuptools import find_packages, setup


#!/usr/bin/env python3
import imp
import os

import setuptools
from pkg_resources import parse_version
from setuptools import setup


def load_module(module_path):
    path = None
    for name in module_path.split("."):
        file, path, description = imp.find_module(name, path)
        path = [path]
    return imp.load_module(name, file, path[0], description)


setup(
    name="Rujaion",
    version="0.5.3",
    author="Ryosuke Fukatani",
    install_requires=[
        "PyQt5",
        "PyQtWebEngine",
        "pexpect",
        "online-judge-tools",
        "pandas",
    ],
    packages=find_packages(exclude=("docker", "doc")),
    package_data={ 'rujaion' : ['resources/*'], },
    entry_points={
        'console_scripts': [
            'rujaion = rujaion.rujaion_main:main',
        ],
    },
)
