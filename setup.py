#!/usr/bin/env python3
import imp
from setuptools import find_packages

from setuptools import setup


def load_module(module_path):
    path = None
    for name in module_path.split("."):
        file, path, description = imp.find_module(name, path)
        path = [path]
    return imp.load_module(name, file, path[0], description)


setup(
    name="Rujaion",
    version="0.14.0",
    author="Ryosuke Fukatani",
    install_requires=[
        "PyQt5",
        "PyQtWebEngine",
        "pexpect",
        "online-judge-tools == 11.1.1",
        "online-judge-api-client == 10.5.0",
        "pandas",
    ],
    packages=find_packages(exclude=("docker", "doc")),
    package_data={"rujaion": ["resources/*"]},
    entry_points={"console_scripts": ["rujaion = rujaion.rujaion_main:main"]},
)
