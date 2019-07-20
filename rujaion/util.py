import os
import subprocess
from typing import *

from PyQt5 import QtWidgets


TEMPFILE = os.path.join(os.path.dirname(__file__), "temp.rs")


def disp_error(message: str):
    error = QtWidgets.QErrorMessage()
    error.showMessage(message)
    error.exec_()


def racer_enable() -> bool:
    try:
        output = subprocess.check_output(("racer", "--version"))
        if output.decode().startswith("racer"):
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False


def debug_command(lang: str) -> str:
    if lang == "rust":
        return "env RUST_BACKTRACE=1 rust-gdb"
    else:
        return "gdb"


def compile_command(lang: str, no_debug: bool) -> List[str]:
    if lang == "rust":
        if no_debug:
            return ["rustc",]
        else:
            return ["rustc", "-g"]
    else:
        if no_debug:
            return ['g++', '-std=gnu++1y', '-O2', '-I/opt/boost/gcc/include', '-L/opt/boost/gcc/lib']
        else:
            return ['g++', '-std=gnu++1y', '-g', '-I/opt/boost/gcc/include', '-L/opt/boost/gcc/lib']


def get_compiled_file(lang: str, fname: str) -> str:
    if lang == "rust":
        return fname.replace(".rs", "")
    else:
        return "a.out"


def exec_format(lang: str) -> bool:
    if lang == "rust":
        try:
            subprocess.check_output(
                ("rustfmt", TEMPFILE), stderr=subprocess.STDOUT
            )
        except Exception:
            return False
    else:
        try:
            subprocess.check_output(
                ("clang-format",  "-i", TEMPFILE), stderr=subprocess.STDOUT
            )
        except Exception:
            return False
    return True


def exec_command(lang: str) -> List[str]:
    if lang == "rust":
        return ["env", "RUST_BACKTRACE=1"]
    else:
        return []


def get_submit_lang(lang: str) -> str:
    if lang == "cpp":
        return "C++14 (GCC 5.4.1)"
    return lang
