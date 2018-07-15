from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QPoint, QEvent


class RustEditter(QtWidgets.QTextEdit):
    doubleClickedSignal = pyqtSignal(QPoint)

    def __init__(self, *args):
        super().__init__(*args)

    def mouseDoubleClickEvent(self, event):
        # if event.type() == QEvent.MouseButtonDblClick:
        self.doubleClickedSignal.emit(event.pos())
