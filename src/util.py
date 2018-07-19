from PyQt5 import QtWidgets

def disp_error(message):
    error = QtWidgets.QErrorMessage()
    error.showMessage(message)
    error.exec_()
