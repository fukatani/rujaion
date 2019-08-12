# From https://www.binpress.com/building-text-editor-pyqt-3/

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt

import re


class FindTextEdit(QtWidgets.QTextEdit):
    def __init__(self, parent, enter_action):
        self.enter_action = enter_action
        super().__init__(parent)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == 16777220:  # Enter
            self.enter_action()
            return
        if e.key() == Qt.Key_Tab:
            self.parent().toggle_focus()
            return
        super().keyPressEvent(e)


class Find(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.lastMatch = None
        self.lastStart = 0
        self.initUI()

    def initUI(self):

        # Button to search the document for something
        findButton = QtWidgets.QPushButton("Find", self)
        findButton.clicked.connect(self.find)

        # Button to replace the last finding
        replaceButton = QtWidgets.QPushButton("Find and Replace", self)
        replaceButton.clicked.connect(self.replace)

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

        # Whole Words option
        self.wholeWords = QtWidgets.QCheckBox("Whole words", self)

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
        layout.addWidget(self.wholeWords, 6, 2)

        self.setGeometry(300, 300, 360, 250)
        self.setWindowTitle("Find and Replace")
        self.setLayout(layout)

        # By default the normal mode is activated
        self.normalRadio.setChecked(True)

    def toggle_focus(self):
        if self.findField.hasFocus():
            self.replaceField.setFocus()
        else:
            self.findField.setFocus()

    def find(self):
        # Grab the parent's text
        text = self.parent.toPlainText()

        # And the text to find
        query = self.findField.toPlainText()

        # If the 'Whole Words' checkbox is checked, we need to append
        # and prepend a non-alphanumeric character
        if self.wholeWords.isChecked():
            query = r"\W" + query + r"\W"

        # By default regexes are case sensitive but usually a search isn't
        # case sensitive by default, so we need to switch this around here
        flags = 0 if self.caseSens.isChecked() else re.I

        if self.normalRadio.isChecked():
            # Use normal string search to find the query from the
            # last starting position
            self.lastStart = text.find(query, self.lastStart + 1)

            # If the find() method didn't return -1 (not found)
            if self.lastStart >= 0:
                end = self.lastStart + len(query)
                self.moveCursor(self.lastStart, end)
            else:
                # Make the next search start from the begining again
                self.lastStart = 0
                # self.moveCursor(QtGui.QTextCursor.atStart())

        else:
            # Compile the pattern
            pattern = re.compile(query, flags)

            start = self.lastMatch.start() + 1 if self.lastMatch else 0

            # The actual search
            self.lastMatch = pattern.search(text, start)
            if self.lastMatch:
                start = self.lastMatch.start()
                end = self.lastMatch.end()

                # If 'Whole words' is checked, the selection would include the two
                # non-alphanumeric characters we included in the search, which need
                # to be removed before marking them.
                if self.wholeWords.isChecked():
                    start += 1
                    end -= 1
                self.moveCursor(start, end)

    def replace(self):
        self.find()

        # Grab the text cursor
        cursor = self.parent.textCursor()

        # Security
        if self.lastMatch and cursor.hasSelection():
            # We insert the new text, which will override the selected
            # text
            cursor.insertText(self.replaceField.toPlainText())

            # And set the new cursor
            self.parent.setTextCursor(cursor)

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
        self.wholeWords.setChecked(False)

        # Then disable them (gray them out)
        self.caseSens.setEnabled(False)
        self.wholeWords.setEnabled(False)

    def normalMode(self):

        # Enable checkboxes (un-gray them)
        self.caseSens.setEnabled(True)
        self.wholeWords.setEnabled(True)

    def moveCursor(self, start, end):

        # We retrieve the QTextCursor object from the parent's QTextEdit
        cursor = self.parent.textCursor()

        # Then we set the position to the beginning of the last match
        cursor.setPosition(start)

        # Next we move the Cursor by over the match and pass the KeepAnchor parameter
        # which will make the cursor select the the match's text
        cursor.movePosition(
            QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start
        )

        # And finally we set this new cursor as the parent's
        self.parent.setTextCursor(cursor)
