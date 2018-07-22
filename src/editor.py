import codecs
from collections import defaultdict
import subprocess

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtCore import Qt

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

class RustEditter(QtWidgets.QPlainTextEdit):
    doubleClickedSignal = pyqtSignal(QPoint)

    def __init__(self, *args):
        super().__init__(*args)
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)

        self.lineNumberAreaWidth = self.fontMetrics().width('8') * 4
        self.setViewportMargins(self.lineNumberAreaWidth, 0, 0, 0)
        self.lineNumberArea = QtWidgets.QWidget(self)
        self.lineNumberArea.installEventFilter(self)

        self.break_points = defaultdict(lambda : False)
        self.edited = False
        self.textChanged.connect(self.set_edited)
        self.fname = ''
        self.completer = RacerCompleter(self)
        self.completer.setWidget(self)
        self.completer.insertText.connect(self.insertCompletion)

    def mouseDoubleClickEvent(self, event):
        self.doubleClickedSignal.emit(event.pos())

    def eventFilter(self, obj, event):
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
            painter.drawText(0, y, self.lineNumberAreaWidth,
                             ht, Qt.AlignRight, disp)
            line_number += 1
            block = block.next()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.lineNumberArea.setGeometry(QtCore.QRect(self.rect().left(),
                                                     self.rect().top(),
                                                     self.lineNumberAreaWidth,
                                                     self.rect().height()))

    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.repaint()

    def toggleBreak(self, line_num):
        self.break_points[line_num] = not self.break_points[line_num]
        self.repaint()

    def generateBreak(self):
        commands = []
        for i in range(1, self.document().blockCount()):
            if self.break_points[i]:
                commands.append(("b " + str(i) + "\n").encode())
        return commands

    def highlight_current_line(self, line_num):
        extraSelections = []
        selection = QtWidgets.QTextEdit.ExtraSelection()
        selection.format.setBackground(Qt.cyan)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection,
                                     QtCore.QVariant(True))
        selection.cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line_num - 1))
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

        self.setTextCursor(selection.cursor)
        self.ensureCursorVisible()

    def clear_highlight_line(self):
        self.setExtraSelections([])

    def open_file(self, fname):
        assert fname
        f = open(fname)
        self.setPlainText(f.read())
        self.edited = False
        self.fname = fname

    def new_file(self, template_file_name=""):
        self.clear()
        self.edited = False
        self.fname = ""
        if template_file_name:
            with open(template_file_name) as f:
                self.setPlainText(f.read())

    def set_edited(self):
        self.edited = True

    # TODO: support multifile
    def jump(self):
        src_line_num = str(self.textCursor().blockNumber() + 1)
        src_char_num = str(self.textCursor().columnNumber())

        try:
            # out = subprocess.check_output(("racer", "find-definition",
            #                                src_line_num, src_char_num,
            #                                self.fname))
            out = subprocess.check_output("racer find-definition" + " " +
                                          src_line_num + " " + src_char_num +
                                          " " + self.fname, shell=True).decode()
        except Exception:
            return
        if not out.startswith("MATCH"):
            return
        out = out[6:]
        words = out.split(",")
        line_num, char_num = int(words[1]), int(words[2])
        cursor = QtGui.QTextCursor(
            self.document().findBlockByLineNumber(line_num - 1))
        cursor.movePosition(QtGui.QTextCursor.NextCharacter,
                            QtGui.QTextCursor.MoveAnchor, char_num)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) - len(self.completer.completionPrefix()))
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)
        self.completer.popup().hide()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        super().focusInEvent(event)

    def keyPressEvent(self, event):

        tc = self.textCursor()
        if event.key() == Qt.Key_Tab and self.completer.popup().isVisible():
            self.completer.insertText.emit(self.completer.getSelected())
            self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
            return

        super().keyPressEvent(event)
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        cr = self.cursorRect()

        if len(tc.selectedText()) > 1:
            self.completer.setCompletionPrefix(tc.selectedText())
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0,0))

            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)
        else:
            self.completer.popup().hide()

class RacerCompleter(QtWidgets.QCompleter):
    insertText = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__((), parent)
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.highlighted.connect(self.setHighlighted)
        self.parent = parent

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected

    # this is heavy?
    def setCompletionPrefix(self, text):
        fname = codecs.open('temp.rs', 'w', 'utf-8')
        fname.write(self.parent.toPlainText())
        fname.close()
        src_line_num = str(self.parent.textCursor().blockNumber() + 1)
        src_char_num = str(self.parent.textCursor().columnNumber())

        try:
            out = subprocess.check_output("racer complete" + " " +
                                          src_line_num + " " + src_char_num +
                                          " temp.rs",
                                          shell=True).decode()
        except Exception:
            return
        candidates = []
        for line in out.split("\n"):
            if line.startswith("MATCH"):
                candidates.append(line[6:].split(",")[0])
        if len(candidates) >= 6 or text in candidates:
            candidates = []
        self.setModel(QtCore.QStringListModel(candidates))
        super().setCompletionPrefix(text)
