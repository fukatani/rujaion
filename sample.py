from PyQt5 import QtWidgets
import syntax

app = QtWidgets.QApplication(['rust'])
editor = QtWidgets.QPlainTextEdit()
highlight = syntax.RustHighlighter(editor.document())
editor.show()

# Load syntax.py into the editor for demo purposes
infile = open('syntax.py', 'r')
editor.setPlainText(infile.read())

app.exec_()