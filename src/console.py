from io import StringIO
from PyQt5 import QtWidgets, QtGui, QtCore


class Console(QtWidgets.QTextEdit):

    def __init__(self, parent=None):
        super(Console, self).__init__(parent)
        self._buffer = StringIO()
        self.setReadOnly(True)

    def write(self, msg, mode=''):
        if isinstance(msg, bytes):
            msg = msg.decode()
        font = QtGui.QFont()
        if mode == '':
            font.setBold(False)
            self.setTextColor(QtCore.Qt.black)
        elif mode == 'success':
            font.setBold(True)
            self.setTextColor(QtCore.Qt.blue)
        elif mode == 'error':
            font.setBold(True)
            self.setTextColor(QtCore.Qt.red)
        elif mode == 'gdb':
            font.setBold(False)
            self.setTextColor(QtCore.Qt.black)
            msg = '>>> ' + msg
        self.setFont(font)
        msg = msg + '\n'
        self.insertPlainText(msg)
        self.moveCursor(QtGui.QTextCursor.End)
        self._buffer.write(msg)

    def test_result_write(self, msg):
        if isinstance(msg, bytes):
            msg = msg.decode()
        for line in msg.split('\n'):
            if line.startswith('[+]'):
                self.write(line, mode="success")
            elif line.startswith('[-]'):
                self.write(line, mode="error")
            else:
                self.write(line)

    def __getattr__(self, attr):
        return getattr(self._buffer, attr)
