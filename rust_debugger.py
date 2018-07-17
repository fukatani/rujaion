import codecs
import os
import subprocess
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import pexpect

import syntax
import editor
import util
import console


# TODO: breakpoint highlight
# TODO: step
# TODO: print
# TODO: watch
# TODO: completer


class CustomMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CustomMainWindow, self).__init__(parent)
        self.resize(800, 700)
        self.setWindowTitle("RustGUIDebugger")
        self.setStyleSheet("background-color: white")
        self.addCentral()

        self.file_tool = self.addToolBar("File")
        self.edit_tool = self.addToolBar("Exit")

        newbutton = self.file_tool.addAction("New...")
        newbutton.triggered.connect(self.newFile)

        openbutton = self.file_tool.addAction("Open...")
        openbutton.triggered.connect(self.showFileDialog)

        savebutton = self.edit_tool.addAction("Save...")
        savebutton.triggered.connect(self.saveFile)

        compilebutton = self.edit_tool.addAction("Compile...")
        compilebutton.triggered.connect(self.compile)

        runbutton = self.edit_tool.addAction("Run...")
        runbutton.triggered.connect(self.run)

        debugbutton = self.edit_tool.addAction("Debug...")
        debugbutton.triggered.connect(self.debug)

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

        self.fname = ''
        self.settings = QtCore.QSettings('RustDebugger', 'RustDebugger')
        self.openFile(self.settings.value('LastOpenedFile', type=str))
        self.addConsole()

    def showFileDialog(self):
        dirname = os.path.dirname(self.settings.value('LastOpenedFile', type=str))
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open', dirname, 'Rust Files (*.rs)')[0]
        self.openFile(fname)

    def openFile(self, fname):
        if not fname:
            return
        f = open(fname)
        self.editor.setPlainText(f.read())
        self.settings.setValue('LastOpenedFile', fname)
        self.fname = fname
        self.setWindowTitle(self.fname)

    def saveFile(self):
        savename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '')[0]
        if not savename:
            return
        fname = codecs.open(savename, 'w', 'utf-8')
        fname.write(self.editor.toPlainText())

    def addEditer(self, parent):
        self.editor = editor.RustEditter(parent)
        self.highlighter = syntax.RustHighlighter(self.editor.document())
        self.editor.doubleClickedSignal.connect(self.OnMousePressed)

    def addCentral(self):
        self.addEditer(self)
        self.setCentralWidget(self.editor)

    def OnMousePressed(self, pos):
        cursor = self.editor.cursorForPosition(pos)
        line_num = cursor.blockNumber() + 1
        self.editor.toggleBreak(line_num)

    def addConsole(self):
        self.bottom_widget = console.Console(self)
        dock = QtWidgets.QDockWidget("Console", self)
        dock.setWidget(self.bottom_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def newFile(self):
        self.editor.clear()

    def compile(self):
        if not self.fname:
            util.disp_error("File is not opened.")
        command = ("rustc", "-g", self.fname)
        try:
            _ = subprocess.check_output(command)
            self.bottom_widget.write('Compile is finished successfully!',
                                     mode='success')
        except subprocess.CalledProcessError as err:
            self.bottom_widget.write(err, mode='error')

    def run(self):
        if not self.fname:
            util.disp_error("File is not opened.")
        compiled_file = os.path.basename(self.fname).replace('.rs', '')
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not opened.")
        try:
            output = subprocess.check_output(('./' + compiled_file,))
            self.bottom_widget.write(output)
        except subprocess.CalledProcessError as err:
            self.bottom_widget.write(err, mode='error')

    def debug(self):
        if not self.fname:
            util.disp_error("File is not opened.")
        compiled_file = os.path.basename(self.fname).replace('.rs', '')
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not opened.")
        try:
            proc = pexpect.spawn('rust-gdb  ./' + compiled_file)

            proc.expect('\(gdb\)')
            self.bottom_widget.write(proc.before.decode())

            for com in self.editer.generateBreak():
                proc.send(com)
                proc.expect('\(gdb\)')
                self.bottom_widget.write(proc.before.decode(), mode='gdb')

            print('run ' + compiled_file)
            proc.send(b'run\n')
            proc.expect('\(gdb\)')
            self.bottom_widget.write(proc.before.decode(), mode='gdb')

            print('quit ' + compiled_file)
            proc.send(b'quit\n')
            proc.terminate()

        except subprocess.CalledProcessError as err:
            self.bottom_widget.write(err, mode='error')


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = CustomMainWindow()
    main.show()
    app.exec_()


if __name__ == '__main__':
    main()
