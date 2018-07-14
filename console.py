from io import StringIO
from PyQt5 import QtWidgets, QtGui


class Console(QtWidgets.QTextEdit):

    def __init__(self, parent=None):
        super(Console, self).__init__(parent)
        self._buffer = StringIO()
        self.setReadOnly(True)

    def write(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode()
        self.insertPlainText(msg)
        self.moveCursor(QtGui.QTextCursor.End)
        self._buffer.write(msg)

    def __getattr__(self, attr):
        return getattr(self._buffer, attr)
