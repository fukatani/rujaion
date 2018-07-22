from collections import defaultdict

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

    def new_file(self):
        self.clear()
        self.edited = False

    def set_edited(self):
        self.edited = True
