#!/usr/bin/env python3
import imp
import os

import setuptools
from pkg_resources import parse_version
from setuptools import setup

if parse_version(setuptools.__version__) < parse_version('30.3.0'):
    raise RuntimeError('setuptools>=30.3.0 is required for "setup.cfg"')


def load_module(module_path):
    path = None
    for name in module_path.split('.'):
        file, path, description = imp.find_module(name, path)
        path = [path]
    return imp.load_module(name, file, path[0], description)

setup(
    name="Rujaion",
    version="0.1",
    author="Ryosuke Fukatani",
)
