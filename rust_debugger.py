import codecs
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import syntax


# TODO: open last opened file
# TODO: compile
# TODO: console
# TODO: run
# TODO: breakpoint
# TODO: step
# TODO: print
# TODO: watch


class CustomMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CustomMainWindow, self).__init__(parent)
        self.resize(800, 700)
        self.setWindowTitle("RustGUIDebugger")
        self.setStyleSheet("background-color: white")
        self.addtextedit()
        self.setCentralWidget(self.editor)

        self.file_tool = self.addToolBar("File")
        self.edit_tool = self.addToolBar("Exit")

        self.newbutton = self.file_tool.addAction("New...")
        self.newbutton.triggered.connect(self.newFile)

        self.openbutton = self.file_tool.addAction("Open...")
        self.openbutton.triggered.connect(self.showFileDialog)

        self.savebutton = self.edit_tool.addAction("Save...")
        self.savebutton.triggered.connect(self.saveFile)

        # closebutton = self.edit_tool.addAction("Close...")
        # self.connect(closebutton, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        # Add MenuBar
        filemenu = self.menuBar()
        filemenu = filemenu.addMenu('&File')
        filemenu.addMenu("New...")
        filemenu.addMenu("Open...")
        filemenu.addMenu("Save...")

        # Add Open menu
        a = QtWidgets.QAction('Open', self)
        a.setShortcut('Ctrl+o')
        a.triggered.connect(self.showFileDialog)
        filemenu.addAction(a)

        # Add Exit menu
        #a = QtWidgets.QAction('Exit', self)
        #a.setShortcut('Ctrl+w')
        #a.triggered.connect(QtCore.SLOT('close()'))
        #filemenu.addAction(a)

        # Add Save menu
        a = QtWidgets.QAction('Save', self)
        a.setShortcut('Ctrl+s')
        a.triggered.connect(self.saveFile)
        filemenu.addAction(a)

        self.settings = QtCore.QSettings('RustDebugger', 'RustDebugger')
        self.openFile(self.settings.value('LastOpenedFile', type=str))

    def showFileDialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open', '.rs')[0]
        if not fname:
            return
        self.openFile(fname)

    def openFile(self, fname):
        f = open(fname)
        self.editor.setPlainText(f.read())
        self.settings.setValue('LastOpenedFile', fname)

    def saveFile(self):
        savename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '')[0]
        if not savename:
            return
        fname = codecs.open(savename, 'w', 'utf-8')
        fname.write(self.editor.toPlainText())

    def addtextedit(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.editor = QtWidgets.QTextEdit()
        self.editor.setFont(font)
        self.highlighter = syntax.RustHighlighter(self.editor.document())

    def newFile(self):
        self.editor.clear()


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = CustomMainWindow()
    main.show()
    app.exec_()


if __name__ == '__main__':
    main()
