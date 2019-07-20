from collections import deque
import sys
from typing import *

from io import StringIO
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
import pexpect

from rujaion.custom_popup import CustomPopup


class Console(QtWidgets.QTextEdit):
    writeOjSignal = pyqtSignal(object)

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
        self.writeOjSignal.connect(self.write_oj_result)
        self.evcxr_proc = None
        self.run_evcxr()

        self.command_history = deque(maxlen=10)
        # HACK
        self.color_words = ("\033[91m", "\033[94m", "\033[0m")
        self.history_pointer = 0
        self.popup = None

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

    def write(self, msg: Union[str, bytes], mode: str = ""):
        self.moveCursor(QtGui.QTextCursor.End)
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
        self._buffer.write(msg)

    def write_oj_result(self, msg: Union[str, bytes]):
        last_submission = None
        if isinstance(msg, bytes):
            msg = msg.decode()
        for line in msg.split("\n"):
            if line.startswith("[+]"):
                submit_result_prefix = "[+] success: result: "
                if line.startswith(submit_result_prefix):
                    last_submission = line[len(submit_result_prefix):]
                self.write(line, mode="success")
            elif line.startswith("[-]"):
                self.write(line, mode="error")
            else:
                self.write(line)
        if last_submission is not None and "atcoder" in last_submission:
            self.popup = CustomPopup(None, url=last_submission)
            self.popup.show()

    def __getattr__(self, attr):
        return getattr(self._buffer, attr)

    def __contextMenu(self):
        menu = self.createStandardContextMenu()
        self._addCustomMenuItems(menu)
        menu.exec_(QtGui.QCursor.pos())

    def _addCustomMenuItems(self, menu: QtWidgets.QMenu):
        menu.addSeparator()
        menu.addAction(u"Clear", self.clear)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        tc = self.textCursor()
        if (
            event.key() == Qt.Key_Up
            and tc.blockNumber() == self.document().blockCount() - 1
        ):
            if self.history_pointer < len(self.command_history) - 1:
                self.history_pointer += 1
            else:
                return
            cur_idx = len(self.command_history) - self.history_pointer
            try:
                last_command = self.command_history[cur_idx]
            except IndexError:
                self.history_pointer = 0
                return
            tc.select(QtGui.QTextCursor.LineUnderCursor)
            tc.removeSelectedText()
            self.display_prefix()
            self.insertPlainText(last_command)
            return
        if (
            event.key() == Qt.Key_Down
            and tc.blockNumber() == self.document().blockCount() - 1
        ):
            if self.history_pointer >= 1:
                self.history_pointer -= 1
            cur_idx = len(self.command_history) - self.history_pointer
            try:
                last_command = self.command_history[cur_idx]
            except IndexError:
                self.history_pointer = 0
                return
            tc.select(QtGui.QTextCursor.LineUnderCursor)
            tc.removeSelectedText()
            self.display_prefix()
            self.insertPlainText(last_command)
            return
        self.history_pointer = 0

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
                self.command_history.append(
                    self.document().toPlainText().split("\n")[-1][3:]
                )
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
