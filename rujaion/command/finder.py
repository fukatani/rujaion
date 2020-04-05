# From https://www.binpress.com/building-text-editor-pyqt-3/

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt

import re


class FindTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent, enter_action):
        self.enter_action = enter_action
        super().__init__(parent)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == Qt.Key_Return:
            self.enter_action()
            return
        if e.key() == Qt.Key_Tab:
            self.parent().toggle_focus()
            return
        super().keyPressEvent(e)


class Find(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lastMatch = None
        self.initUI()

    def initUI(self):

        # Button to search the document for something
        findButton = QtWidgets.QPushButton("Find", self)
        findButton.clicked.connect(self.find)

        # Button to replace the last finding
        replaceButton = QtWidgets.QPushButton("Find and Replace", self)
        replaceButton.clicked.connect(self.findAndReplace)

        # Button to remove all findings
        allButton = QtWidgets.QPushButton("Replace all", self)
        allButton.clicked.connect(self.replaceAll)

        # Normal mode - radio button
        self.normalRadio = QtWidgets.QRadioButton("Normal", self)
        self.normalRadio.toggled.connect(self.normalMode)

        # Regular Expression Mode - radio button
        self.regexRadio = QtWidgets.QRadioButton("RegEx", self)
        self.regexRadio.toggled.connect(self.regexMode)

        # The field into which to type the query
        self.findField = FindTextEdit(self, self.find)
        self.findField.resize(250, 50)
        self.findField.setFocus()

        # The field into which to type the text to replace the
        # queried text
        self.replaceField = FindTextEdit(self, self.replace)
        self.replaceField.resize(250, 50)

        optionsLabel = QtWidgets.QLabel("Options: ", self)

        # Case Sensitivity option
        self.caseSens = QtWidgets.QCheckBox("Case sensitive", self)

        # Layout the objects on the screen
        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.findField, 1, 0, 1, 4)
        layout.addWidget(self.normalRadio, 2, 2)
        layout.addWidget(self.regexRadio, 2, 3)
        layout.addWidget(findButton, 2, 0, 1, 2)

        layout.addWidget(self.replaceField, 3, 0, 1, 4)
        layout.addWidget(replaceButton, 4, 0, 1, 2)
        layout.addWidget(allButton, 4, 2, 1, 2)

        # Add some spacing
        spacer = QtWidgets.QWidget(self)
        spacer.setFixedSize(0, 10)

        layout.addWidget(spacer, 5, 0)
        layout.addWidget(optionsLabel, 6, 0)
        layout.addWidget(self.caseSens, 6, 1)

        self.setGeometry(300, 300, 360, 250)
        self.setWindowTitle("Find and Replace")
        self.setLayout(layout)

        # By default the normal mode is activated
        self.normalRadio.setChecked(True)

    def toggle_focus(self):
        if self.findField.hasFocus():
            self.replaceField.setFocus()
            self.replaceField.selectAll()
        else:
            self.findField.setFocus()
            self.findField.selectAll()

    def find(self):
        # Grab the parent's text
        text = self.parent().toPlainText()

        # And the text to find
        query = self.findField.toPlainText()

        # By default regexes are case sensitive but usually a search isn't
        # case sensitive by default, so we need to switch this around here
        flags = 0 if self.caseSens.isChecked() else re.I

        # Compile the pattern
        if self.normalRadio.isChecked():
            pattern = re.compile(re.escape(query), flags)
        else:
            pattern = re.compile(query, flags)
        start = self.lastMatch.start() + 1 if self.lastMatch else 0

        # The actual search
        self.lastMatch = pattern.search(text, start)
        if self.lastMatch:
            start = self.lastMatch.start()
            end = self.lastMatch.end()
            self.moveCursor(start, end)

    def findAndReplace(self):
        self.find()
        self.replace()

    def replace(self):
        cursor = self.parent().textCursor()

        if self.lastMatch and cursor.hasSelection():
            cursor.insertText(self.replaceField.toPlainText())
            self.parent().setTextCursor(cursor)

    def replaceAll(self):
        # Initial find() call so that lastMatch is
        # potentially not None anymore
        self.find()

        # Replace and find until find is None again
        while self.lastMatch:
            self.replace()
            self.find()

    def regexMode(self):

        # First uncheck the checkboxes
        self.caseSens.setChecked(False)

        # Then disable them (gray them out)
        self.caseSens.setEnabled(False)

    def normalMode(self):

        # Enable checkboxes (un-gray them)
        self.caseSens.setEnabled(True)

    def moveCursor(self, start, end):

        # We retrieve the QTextCursor object from the parent's QTextEdit
        cursor = self.parent().textCursor()

        # Then we set the position to the beginning of the last match
        cursor.setPosition(start)

        # Next we move the Cursor by over the match and pass the KeepAnchor parameter
        # which will make the cursor select the the match's text
        cursor.movePosition(
            QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start
        )

        # And finally we set this new cursor as the parent's
        self.parent().setTextCursor(cursor)
