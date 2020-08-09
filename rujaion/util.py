import os
import re
import subprocess
from typing import *

import pexpect
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QMutex


def get_temp_file(lang: str):
    if lang == "rust":
        return os.path.join(os.path.dirname(__file__), "temp.rs")
    if lang == "python3":
        return os.path.join(os.path.dirname(__file__), "temp.py")
    else:
        return os.path.join(os.path.dirname(__file__), "temp.cpp")


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
    if lang == "python3":
        return "python3 -m pdb"
    else:
        return "gdb"


def compile_command(lang: str, no_debug: bool) -> List[str]:
    if lang == "rust":
        if no_debug:
            return ["rustc"]
        else:
            return ["rustc", "-g"]
    elif lang == "python3":
        checker = os.path.join(os.path.dirname(__file__), "py_syntax_checker.py")
        return ["python3", checker]
    else:
        if no_debug:
            return [
                "g++",
                "-std=gnu++1y",
                "-O2",
                "-fsanitize=undefined",
                "-I/opt/boost/gcc/include",
                "-L/opt/boost/gcc/lib",
            ]
        else:
            return [
                "g++",
                "-std=gnu++1y",
                "-fsanitize=undefined",
                "-g",
                "-I/opt/boost/gcc/include",
                "-L/opt/boost/gcc/lib",
            ]


def get_compiled_file(lang: str, fname: str) -> str:
    if lang == "rust":
        return "./" + os.path.basename(fname.replace(".rs", ""))
    elif lang == "python3":
        return fname
    else:
        return "./a.out"


def exec_format(lang: str) -> bool:
    tempfile = get_temp_file(lang)
    if lang == "rust":
        try:
            subprocess.check_output(("rustfmt", tempfile), stderr=subprocess.STDOUT)
        except Exception:
            return False
    elif lang == "python3":
        try:
            subprocess.check_output(
                ("autopep8", "-i", tempfile), stderr=subprocess.STDOUT
            )
        except Exception:
            return False
    else:
        try:
            subprocess.check_output(
                ("clang-format", "-i", tempfile), stderr=subprocess.STDOUT
            )
        except Exception:
            return False
    return True


def exec_command(lang: str) -> List[str]:
    if lang == "rust":
        return ["env", "RUST_BACKTRACE=1"]
    elif lang == "python3":
        return ["python3"]
    else:
        return []


def indent_width(lang: str) -> int:
    if lang == "rust" or lang == "python3":
        return 4
    else:
        return 2


class StateLessTextEdit(QtWidgets.QLineEdit):
    def __init__(self, value: str, parent):
        super().__init__()
        self.parent = parent
        self.setText(value)


# Need to call commit to serialize value
class StateFullTextEdit(QtWidgets.QLineEdit):
    def __init__(self, settings, name: str, parent, default: Optional[str] = None):
        super().__init__()
        self.parent = parent
        self.settings = settings
        self.name = name
        v = settings.value(name, type=str)
        self.setText(v)
        if not v and default is not None:
            self.setText(default)

    def commit(self):
        self.settings.setValue(self.name, self.text())


class StateFullCheckBox(QtWidgets.QCheckBox):
    def __init__(self, settings, name: str, parent):
        super().__init__()
        self.parent = parent
        self.settings = settings
        self.name = name
        v = settings.value(name, type=bool)
        self.setChecked(v)

    def commit(self):
        self.settings.setValue(self.name, self.isChecked())


def get_resources_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "resources")


def wait_input_ready(
    debug_process: pexpect.spawn, lang: str, timeout: Optional[float] = None
):
    if lang == "python3":
        debug_process.expect("\(Pdb\)", timeout=timeout)
    else:
        debug_process.expect("\(gdb\)", timeout=timeout)


def get_executing_line(lang: str, line: str) -> Optional[int]:
    if lang == "python3":
        if line.endswith("<module>()"):
            match = re.search(r"(\()(.*?)\)", line)
            return int(match.groups()[-1])
    else:
        try:
            line_num = int(line.split("\t")[0])
            return line_num
        except ValueError:
            return None
    return None


class WriteObj(object):
    def __init__(self, msg: Union[bytes, str], mode: str = ""):
        self.msg = msg
        self.mode = mode


OJ_MUTEX = QMutex()


class Commander(QThread):
    def __init__(self, console):
        super().__init__()
        self.console = console
        self.cmd = ""

    def run(self):
        OJ_MUTEX.lock()
        try:
            out = subprocess.check_output(self.cmd, stderr=subprocess.STDOUT).decode()
            self.console.writeLnSignal.emit(out)
        except subprocess.CalledProcessError as err:
            self.console.writeLnSignal.emit(err.output)
        scroll_bar = self.console.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        OJ_MUTEX.unlock()
