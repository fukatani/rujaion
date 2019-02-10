import subprocess

from PyQt5 import QtWidgets


def disp_error(message):
    error = QtWidgets.QErrorMessage()
    error.showMessage(message)
    error.exec_()


def racer_enable():
    try:
        output = subprocess.check_output(("racer", "--version"))
        if output.decode().startswith("racer"):
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False


def rustsym_enable():
    try:
        output = subprocess.check_output(("rustsym", "--version"))
        if output.decode().startswith("rustsym"):
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False
