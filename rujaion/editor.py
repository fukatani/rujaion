import codecs
from collections import defaultdict
import os
import subprocess
from typing import *

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt

from rujaion import completer
from rujaion.command import finder
from rujaion import syntax
from rujaion import util

"""
Fixing Some Bugs on a Sunday Evening
------------------------------------

Whose bugs these are I think I know,
But now he works at 3DO;
He will not see me working here
To fix his code and make it go.

The saner folk must think it queer
To trace without the source code near
After a launch and frozen mouse
The weirdest stack crawl of the year.

I give my nodding head a shake
To see if I can stay awake
The only other thing to do
Is find some more coffeine to take.

This bug is pretty hard to nip,
But I have other ones to fix,
And tons to go before we ship,
And tons to go before we ship.


Written by David A. Lyons <dlyons@apple.com>, January 1994
(with apologies to Robert Frost)

Hey, it's fiction.  Close to reality in spirit,
but does not refer to a specific project, bug, Sunday,
or brand of soft drink.
"""


class Editter(QtWidgets.QPlainTextEdit):
    toggleBreakSignal = pyqtSignal(bytes)

    def __init__(self, *args):
        super().__init__(*args)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)

        self.lineNumberAreaWidth = self.fontMetrics().width("8") * 4
        self.setViewportMargins(self.lineNumberAreaWidth, 0, 0, 0)
        self.lineNumberArea = QtWidgets.QWidget(self)
        self.lineNumberArea.installEventFilter(self)

        self.break_points = defaultdict(lambda: False)
        self.edited = False
        self.textChanged.connect(self.set_edited)
        self.fname = ""

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__contextMenu)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.compile_error_selections = []

        self.lang = "rust"
        self.reset_lang()
        self.cursorPositionChanged.connect(self.highlight_cursor_line)
        self.first_error = None

    def __contextMenu(self):
        self._normalMenu = self.createStandardContextMenu()
        self._addCustomMenuItems(self._normalMenu)
        self._normalMenu.exec_(QtGui.QCursor.pos())

    def _addCustomMenuItems(self, menu: QtWidgets.QMenu):
        menu.addSeparator()
        menu.addAction(u"Go to declaration (Ctrl + b)", self.go_to_declaration)
        if (
            self.textCursor().selectedText()
            and "\u2029" not in self.textCursor().selectedText()
        ):
            menu.addAction(u"Add to watches", self.add_to_watch)

    def add_to_watch(self):
        var = self.textCursor().selectedText()
        self.parent().display_widget.add_var(var)

    def find(self):
        finder.Find(self).show()

    def default_file_name(self) -> str:
        if self.lang == "c++":
            return "test1.cpp"
        else:
            return "test1.rs"

    def highlight_cursor_line(self):
        if self.parent().debug_process is not None:
            return
        extra_selections = []
        selection = QtWidgets.QTextEdit.ExtraSelection()
        line_color = QtGui.QColor(Qt.yellow).lighter(180)

        selection.format.setBackground(line_color)
        selection.format.setProperty(
            QtGui.QTextFormat.FullWidthSelection, QtCore.QVariant(True)
        )
        selection.cursor = self.textCursor()
        # selection.cursor.clearSelection()
        extra_selections.append(selection)
        self.setExtraSelections(extra_selections + self.compile_error_selections)

    def highlight_compile_error(self, highlight_places, is_warning: bool):
        if is_warning:
            line_color = QtGui.QColor(Qt.yellow).darker(180)
        else:
            line_color = QtGui.QColor(Qt.red).lighter(110)
        for line, pos in highlight_places:
            self.add_highlight_error(line, line_color, pos)
        self.setExtraSelections(self.compile_error_selections)

    def reset_compile_info(self):
        self.compile_error_selections.clear()
        self.first_error = None

    def add_highlight_error(self, line: int, line_color: QtGui.QColor, pos: int):
        selection = QtWidgets.QTextEdit.ExtraSelection()
        selection.format.setFontUnderline(True)
        selection.format.setUnderlineColor(line_color)
        selection.format.setUnderlineStyle(QtGui.QTextCharFormat.WaveUnderline)
        selection.format.setProperty(
            QtGui.QTextFormat.FullWidthSelection, QtCore.QVariant(True)
        )
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line - 1))
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        cursor.movePosition(
            QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, pos - 1
        )
        # self.setTextCursor(cursor)
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        selection.cursor = cursor
        self.compile_error_selections.append(selection)
        self.first_error = (line, pos)

    def eventFilter(self, obj, event: QtGui.QKeyEvent) -> bool:
        if obj is self.lineNumberArea and event.type() == QtCore.QEvent.Paint:
            self.drawLineNumbers()
            return True
        return False

    def drawLineNumbers(self):
        painter = QtGui.QPainter(self.lineNumberArea)
        painter.setPen(Qt.black)
        r = QtCore.QRect(self.lineNumberArea.rect())
        painter.fillRect(r, Qt.lightGray)
        ht = self.fontMetrics().height()
        block = QtGui.QTextBlock(self.firstVisibleBlock())
        line_number = block.blockNumber() + 1
        while block.isValid():
            y = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            if y >= r.bottom():
                break
            if self.break_points[line_number]:
                disp = "b " + str(line_number)
            else:
                disp = str(line_number)
            painter.drawText(0, y, self.lineNumberAreaWidth, ht, Qt.AlignRight, disp)
            line_number += 1
            block = block.next()

    def resizeEvent(self, event: QtGui.QKeyEvent):
        super().resizeEvent(event)
        self.lineNumberArea.setGeometry(
            QtCore.QRect(
                self.rect().left(),
                self.rect().top(),
                self.lineNumberAreaWidth,
                self.rect().height(),
            )
        )

    def wheelEvent(self, event: QtGui.QKeyEvent):
        super().wheelEvent(event)
        self.repaint()

    def toggleBreak(self, line_num: int):
        self.break_points[line_num] = not self.break_points[line_num]
        self.repaint()
        if self.break_points[line_num]:
            command = ("b " + str(line_num) + "\n").encode()
        else:
            command = (str(line_num)).encode()
        self.toggleBreakSignal.emit(command)

    def generateBreak(self):
        commands = []
        for i in range(1, self.document().blockCount()):
            if self.break_points[i]:
                commands.append(("b " + str(i) + "\n").encode())
        return commands

    def highlight_executing_line(self, line_num: int):
        extraSelections = []
        selection = QtWidgets.QTextEdit.ExtraSelection()
        selection.format.setBackground(Qt.cyan)
        selection.format.setProperty(
            QtGui.QTextFormat.FullWidthSelection, QtCore.QVariant(True)
        )
        selection.cursor = QtGui.QTextCursor(
            self.document().findBlockByLineNumber(line_num - 1)
        )
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

        self.setTextCursor(selection.cursor)
        self.ensureCursorVisible()

    def clear_highlight_line(self):
        self.setExtraSelections([])

    def open_file(self, fname: str):
        assert fname
        with open(fname) as f:
            self.setPlainText(f.read())
        self.edited = False
        self.fname = fname
        self.reset_lang()

    def reset_file_name(self):
        if self.fname:
            default_dir = os.path.dirname(self.fname)
        else:
            default_dir = os.path.dirname(__file__) + "/rust_sample"
        self.fname = os.path.join(default_dir, self.default_file_name())

    def reset_lang(self, fname: Optional[str] = None):
        if fname is None:
            fname = self.fname
        if fname.endswith("cpp") or fname.endswith("cc"):
            self.lang = "c++"
        elif fname.endswith("py"):
            self.lang = "python3"
        else:
            self.lang = "rust"

        if self.lang == "rust":
            self.completer = completer.RacerCompleter(self)
            self.highlighter = syntax.RustHighlighter(self.document())
        elif self.lang == "python3":
            self.completer = completer.PyCompleter(self)
            self.highlighter = syntax.PyHighlighter(self.document())
        else:
            self.completer = completer.CppCompleter(self)
            self.highlighter = syntax.CppHighlighter(self.document())
        self.completer.setWidget(self)
        self.parent().lang_box.setCurrentText(self.lang)

    def new_file(self, template_file_name: str):
        self.break_points = defaultdict(lambda: False)
        self.clear()
        self.edited = False
        self.reset_lang(template_file_name)
        self.reset_file_name()
        with open(template_file_name) as f:
            self.setPlainText(f.read())
        self.repaint()

    def set_edited(self):
        self.edited = True

    def go_to_declaration(self):
        if self.lang != "rust":
            # Not supported
            return
        src_line_num = str(self.textCursor().blockNumber() + 1)
        src_char_num = str(self.textCursor().columnNumber())

        try:
            # out = subprocess.check_output(("racer", "find-definition",
            #                                src_line_num, src_char_num,
            #                                self.fname))
            out = subprocess.check_output(
                "racer find-definition"
                + " "
                + src_line_num
                + " "
                + src_char_num
                + " "
                + self.fname,
                shell=True,
            ).decode()
        except Exception:
            return
        if not out.startswith("MATCH"):
            return
        out = out[6:]
        words = out.split(",")
        line_num, char_num = int(words[1]), int(words[2])
        self.go_to(line_num, char_num)

    def go_to(self, line_num, char_num):
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line_num - 1))
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.MoveAnchor, char_num
        )
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def go_to_first_error(self):
        if self.first_error is None:
            return
        line_num, char_num = self.first_error
        self.go_to(line_num, char_num)

    def insertCompletion(self):
        text = self.completer.getSelected()
        if text not in self.completer.candidates_dict:  # Not selected from pop up
            self.completer.popup().hide()
            return

        tc = self.textCursor()

        # First we should remove char since some live templates'
        # completion does not start with completion prefix.
        for i in range(len(self.completer.completionPrefix())):
            tc.movePosition(QtGui.QTextCursor.Left)
            tc.deleteChar()

        # tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(text)
        if self.completer.candidates_dict[text] != -1:
            for _ in range(self.completer.candidates_dict[text]):
                tc.movePosition(QtGui.QTextCursor.Left)
        self.setTextCursor(tc)
        self.completer.popup().hide()

    def enter_with_auto_indent(self):
        line_number = self.textCursor().blockNumber()
        line_text = self.document().findBlockByLineNumber(line_number).text()
        indent_level = line_text.count(" " * util.indent_width(self.lang))
        if self.lang == "python3":
            if line_text.endswith(":"):
                indent_level += 1
        elif line_text.endswith("{"):
            indent_level += 1
        self.insertPlainText("\n" + " " * util.indent_width(self.lang) * indent_level)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        tc = self.textCursor()
        if event.key() == 16777220 and self.completer.popup().isVisible():
            self.insertCompletion()
            self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            return

        if event.key() == 16777220:  # Enter
            self.enter_with_auto_indent()
            return

        if event.key() == Qt.Key_BraceRight:
            # Decrease indent level
            if (
                tc.position() > 0
                and self.document().characterAt(tc.position() - 1) != "{"
            ):
                tc.movePosition(QtGui.QTextCursor.StartOfLine)
                for i in range(4):
                    if self.document().characterAt(tc.position()) == " ":
                        tc.deleteChar()

        if event.key() == Qt.Key_F5:
            line_num = tc.blockNumber() + 1
            self.toggleBreak(line_num)
            return

        # comment out or uncomment
        if (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == Qt.Key_Slash
        ):
            tc = self.textCursor()
            if tc.selection().isEmpty():
                selected_line_num = 1
            else:
                selected_line_num = tc.selection().toPlainText().count("\n") + 1
            for i in range(selected_line_num):
                tc.movePosition(QtGui.QTextCursor.StartOfLine)
                if self.document().characterAt(tc.position()) == " ":
                    tc.movePosition(
                        QtGui.QTextCursor.NextWord, QtGui.QTextCursor.MoveAnchor, 1
                    )
                if (
                    self.document().characterAt(tc.position()) == "/"
                    and self.document().characterAt(tc.position() + 1) == "/"
                    and self.document().characterAt(tc.position() + 2) == " "
                ):
                    tc.deleteChar()
                    tc.deleteChar()
                    tc.deleteChar()
                else:
                    tc.insertText("// ")
                tc.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, 1)
            return

        if event.key() == Qt.Key_Tab and event.modifiers() == QtCore.Qt.ControlModifier:
            tc = self.textCursor()
            if tc.selection().isEmpty():
                selected_line_num = 1
            else:
                selected_line_num = tc.selection().toPlainText().count("\n") + 1
            for i in range(selected_line_num):
                tc.movePosition(QtGui.QTextCursor.StartOfLine)
                if self.document().characterAt(tc.position()) == " ":
                    tc.deleteChar()
                    tc.deleteChar()
                    tc.deleteChar()
                    tc.deleteChar()
                    tc.movePosition(
                        QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, 1
                    )
            return

        if event.key() == Qt.Key_Tab:
            tc = self.textCursor()
            if tc.selection().isEmpty():
                selected_line_num = 1
            else:
                selected_line_num = tc.selection().toPlainText().count("\n") + 1
            for i in range(selected_line_num):
                tc.movePosition(QtGui.QTextCursor.StartOfLine)
                tc.insertText(" " * util.indent_width(self.lang))
                tc.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, 1)
            return

        if event.key() == Qt.Key_K and event.modifiers() == QtCore.Qt.ControlModifier:
            self.remove_whole_line()
            return
        if (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_B
        ):
            self.go_to_declaration()
            return
        if event.key() == QtCore.Qt.Key_F2:
            self.go_to_first_error()
            return

        super().keyPressEvent(event)

        if event.key() == Qt.Key_Home:
            if self.textCursor().selectedText():
                return
            if self.document().characterAt(self.textCursor().position()) == " ":
                cursor = self.textCursor()
                cursor.movePosition(
                    QtGui.QTextCursor.NextWord, QtGui.QTextCursor.MoveAnchor, 1
                )
                self.setTextCursor(cursor)

        self.start_complete_process(event, tc)

    # TODO here is slow.
    def start_complete_process(self, event: QtGui.QKeyEvent, tc: QtGui.QTextCursor):
        if (
            event.text().isalnum()
            and not self.document().characterAt(tc.position() + 1).isalnum()
        ):
            tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor, 1)
            tc.select(QtGui.QTextCursor.WordUnderCursor)
            if len(tc.selectedText()) <= 1:
                return
            self.completer.setCompletionPrefix(tc.selectedText())
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
            cr = self.cursorRect()
            cr.setWidth(
                self.completer.popup().sizeHintForColumn(0)
                + self.completer.popup().verticalScrollBar().sizeHint().width()
            )
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()

    def remove_whole_line(self):
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

    def save_pre_process(self):
        # Get formatted Text
        temp_file = codecs.open(util.TEMPFILE, "w", "utf-8")
        temp_file.write(self.toPlainText())
        temp_file.close()
        if not util.exec_format(self.lang):
            return
        temp_file = codecs.open(util.TEMPFILE, "r", "utf-8")
        all_text = "".join([line for line in temp_file.readlines()])
        temp_file.close()

        # Save cursor and scroll bar status
        cursor = self.textCursor()
        line_num = cursor.blockNumber()
        char_num = cursor.columnNumber()
        scroll_value = self.verticalScrollBar().value()

        # Clear all Text and insert format result
        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor, 1)
        cursor.removeSelectedText()
        self.insertPlainText(all_text)

        # recover cursor and scroll bar status
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line_num))
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.MoveAnchor, char_num
        )
        self.setTextCursor(cursor)
        self.verticalScrollBar().setValue(scroll_value)
        self.edited = False
        self.repaint()
