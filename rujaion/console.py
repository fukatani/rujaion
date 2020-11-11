from collections import deque
import sys
from typing import *

from io import StringIO
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
import pexpect
from onlinejudge_workaround_for_conflict.dispatch import submission_from_url

from rujaion.custom_popup import CustomPopup
from rujaion.table_view import TableView
from rujaion.util import WriteObj


class Console(QtWidgets.QTextEdit):
    writeLnSignal = pyqtSignal(object)
    writeSignal = pyqtSignal(object)

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
        self.writeLnSignal.connect(self.__write_by_line)
        self.writeSignal.connect(self.__write)
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
            self.writeLnSignal.emit(e.value)
            return
        self.evcxr_proc.expect(">> ")
        self.writeLnSignal.emit(self.evcxr_proc.before.decode())
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

    def __write(self, write_obj: WriteObj):
        msg = write_obj.msg
        mode = write_obj.mode
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

    def __write_by_line(self, msg: Union[str, bytes]):
        if isinstance(msg, bytes):
            msg = msg.decode()
        for line in msg.split("\n"):
            if line.startswith("[INFO]"):
                self.__write(WriteObj("[*]" + line[6:]))
            elif line.startswith("[+]"):
                self.__write(WriteObj(line, mode="success"))
            elif line.startswith("[SUCCESS]"):
                self.__write(WriteObj("[+]" + line[9:], mode="success"))
            elif (
                line.startswith("[FAILURE]")
            ):
                self.__write(WriteObj("[-]" + line[9:], mode="error"))
            elif (
                line.startswith("[ERROR]")
            ):
                self.__write(WriteObj("[0]" + line[7:], mode="error"))
            else:
                self.__write(WriteObj(line))

    def __getattr__(self, attr):
        return getattr(self._buffer, attr)

    def __contextMenu(self):
        menu = self.createStandardContextMenu()
        self._addCustomMenuItems(menu)
        menu.exec_(QtGui.QCursor.pos())

    def _addCustomMenuItems(self, menu: QtWidgets.QMenu):
        menu.addSeparator()
        menu.addAction(u"Clear", self.clear)
        menu.addAction(u"Visualize Table", self.visualize_table)

    def visualize_table(self):
        tc = self.textCursor()
        self.tv = TableView()
        self.tv.visualize_tables(tc.selectedText())
        self.tv.show()

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
        if event.key() == Qt.Key_Return:
            if self.evcxr_proc is not None:
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
                self.writeLnSignal.emit("\n" + line)
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
