import sys
from io import StringIO
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt

import pexpect


class Console(QtWidgets.QTextEdit):
    def __init__(self, parent=None):
        super(Console, self).__init__(parent)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setFixedPitch(True)
        font.setPointSize(9)
        self.setFont(font)

        self._buffer = StringIO()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
        self.evcxr_proc = None
        self.run_evcxr()
        # HACK
        self.color_words = ("\033[91m", "\033[94m", "\033[0m")

    def run_evcxr(self):
        if self.evcxr_proc is not None:
            self.evcxr_proc.terminate()

        try:
            self.evcxr_proc = pexpect.spawn("evcxr")
        except pexpect.exceptions.ExceptionPexpect as e:
            self.write(e.value)
            return
        self.evcxr_proc.expect(">> ")
        self.write(self.evcxr_proc.before.decode())
        self.display_prefix()

    def terminate_evcxr(self):
        if self.evcxr_proc is None:
            return
        self.evcxr_proc.terminate()
        self.evcxr_proc = None

    def display_prefix(self):
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.EndOfLine)
        tc.insertText("\n>> ")
        tc.movePosition(QtGui.QTextCursor.EndOfBlock)
        tc.movePosition(QtGui.QTextCursor.EndOfLine)
        self.ensureCursorVisible()

    def write(self, msg, mode: str=""):
        if isinstance(msg, bytes):
            msg = msg.decode()
        font = QtGui.QFont()
        if mode == "":
            font.setBold(False)
            self.setTextColor(QtCore.Qt.black)
        elif mode == "success":
            font.setBold(True)
            self.setTextColor(QtCore.Qt.blue)
        elif mode == "error":
            font.setBold(True)
            self.setTextColor(QtCore.Qt.red)
        elif mode == "gdb":
            font.setBold(False)
            self.setTextColor(QtCore.Qt.black)
            msg = "(gdb) " + msg
        self.setFont(font)
        msg = msg + "\n"
        self.insertPlainText(msg)
        self.moveCursor(QtGui.QTextCursor.End)
        self._buffer.write(msg)

    def test_result_write(self, msg: str):
        if isinstance(msg, bytes):
            msg = msg.decode()
        for line in msg.split("\n"):
            if line.startswith("[+]"):
                self.write(line, mode="success")
            elif line.startswith("[-]"):
                self.write(line, mode="error")
            else:
                self.write(line)

    def __getattr__(self, attr):
        return getattr(self._buffer, attr)

    def __contextMenu(self):
        self._normalMenu = self.createStandardContextMenu()
        self._addCustomMenuItems(self._normalMenu)
        self._normalMenu.exec_(QtGui.QCursor.pos())

    def _addCustomMenuItems(self, menu):
        menu.addSeparator()
        menu.addAction(u"Clear", self.clear)

    def keyPressEvent(self, event):
        tc = self.textCursor()

        if (
            event.key() == Qt.Key_Left
            and tc.blockNumber() == self.document().blockCount() - 1
            and tc.columnNumber() <= 3
            and self.evcxr_proc is not None
        ):
            return
        if event.key() in (
            Qt.Key_Left,
            Qt.Key_Right,
            Qt.Key_Up,
            Qt.Key_Down,
            Qt.Key_PageUp,
            Qt.Key_PageDown,
            Qt.Key_Home,
            Qt.Key_End,
        ):
            super().keyPressEvent(event)
            return

        if event.modifiers() == QtCore.Qt.ControlModifier:
            super().keyPressEvent(event)
            return

        # Editable final line only.
        if tc.blockNumber() != self.document().blockCount() - 1:
            return
        if event.key() == 16777220:
            if self.evcxr_proc is not None:
                print("execute")
                command = self.document().toPlainText().split("\n")[-1][3:] + "\n"
                self.evcxr_proc.send(command.encode())
                # self.evcxr_proc.send(b'println!("hello")\n')
                self.evcxr_proc.expect(">> ")

                line = "\n".join(self.evcxr_proc.before.decode().split("\r\n")[1:-1])
                for word in self.color_words:
                    line = line.replace(word, "")
                self.write("\n" + line)

                self.display_prefix()

            return
        super().keyPressEvent(event)


class QMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.console = Console()
        self.setCentralWidget(self.console)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = QMainWindow()
    main.show()
    app.exec_()
