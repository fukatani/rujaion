from collections import defaultdict

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtCore import Qt


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
        self.setReadOnly(True)
        self.setFixedWidth(30)
        self.break_points = defaultdict(lambda: False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def mouseDoubleClickEvent(self, event):
        self.doubleClickedSignal.emit(event.pos())

    def toggleBreak(self, line_num):
        self.break_points[line_num] = not self.break_points[line_num]
        self.update()

    def update(self):
        lines = []
        for i in range(1, 100):
            if self.break_points[i]:
                lines.append('b')
            else:
                lines.append('')
        self.setPlainText('\n'.join(lines))

    def generateBreak(self):
        commands = []
        for i in range(1, 100):
            if self.break_points[i]:
                commands.append(("b " + str(i) + "\n").encode())
        return commands
