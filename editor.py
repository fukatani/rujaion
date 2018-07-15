from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QPoint


class RustEditter(QtWidgets.QTextEdit):
    doubleClickedSignal = pyqtSignal(QPoint)

    def __init__(self, *args):
        super().__init__(*args)

    def mouseDoubleClickEvent(self, event):
        self.doubleClickedSignal.emit(event.pos())


class BreakPointEditter(QtWidgets.QTextEdit):
    doubleClickedSignal = pyqtSignal(QPoint)

    def __init__(self, *args):
        super().__init__(*args)

    def mouseDoubleClickEvent(self, event):
        self.doubleClickedSignal.emit(event.pos())