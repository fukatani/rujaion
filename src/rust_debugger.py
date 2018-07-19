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


# TODO: print
# TODO: watch
# TODO  page
# TODO: completer


class CustomMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(CustomMainWindow, self).__init__(parent)

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

        # compilebutton = self.edit_tool.addAction("Compile...")
        # compilebutton.triggered.connect(self.compile)

        runbutton = self.edit_tool.addAction("Run...")
        runbutton.triggered.connect(self.run)

        debugbutton = self.edit_tool.addAction("Debug...")
        debugbutton.triggered.connect(self.debug)

        continuebutton = self.edit_tool.addAction("Continue...")
        continuebutton.triggered.connect(self.continue_process)

        nextbutton = self.edit_tool.addAction("Next...")
        nextbutton.triggered.connect(self.next)

        stepinbutton =  self.edit_tool.addAction("Step In...")
        stepinbutton.triggered.connect(self.stepIn)

        stepoutbutton = self.edit_tool.addAction("Step Out...")
        stepoutbutton.triggered.connect(self.stepOut)

        terminatebutton = self.edit_tool.addAction("Terminate...")
        terminatebutton.triggered.connect(self.terminate)

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
        self.proc = None
        self.settings = QtCore.QSettings('RustDebugger', 'RustDebugger')
        self.openFile(self.settings.value('LastOpenedFile', type=str))
        self.resize(self.settings.value("size", QtCore.QSize(1000, 900)))
        self.move(self.settings.value("pos", QtCore.QPoint(50, 50)))
        self.addConsole()

    def closeEvent(self, e):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()

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
            return False
        return True

    def run(self):
        if not self.compile():
            return
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
        if not self.compile():
            return
        if not self.fname:
            util.disp_error("File is not opened.")
        compiled_file = os.path.basename(self.fname).replace('.rs', '')
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not opened.")
        try:
            if self.proc is None:
                self.proc = pexpect.spawn('rust-gdb  ./' + compiled_file)
            else:
                self.terminate()
            self.proc.expect('\(gdb\)')
            self.bottom_widget.write(self.proc.before.decode())

            for com in self.editor.generateBreak():
                self.proc.send(com)
                self.proc.expect('\(gdb\)')
                self.bottom_widget.write(self.proc.before.decode(), mode='gdb')

            print('run ' + compiled_file)
            self.proc.send(b'run\n')
            self.post_process()

        except subprocess.CalledProcessError as err:
            self.bottom_widget.write(err, mode='error')


    def next(self):
        print('next')
        if self.proc is None:
            return
        self.proc.send(b'n\n')
        self.post_process()

    def stepIn(self):
        print('step in')
        if self.proc is None:
            return
        self.proc.send(b's\n')
        self.post_process()

    def stepOut(self):
        print('step out')
        if self.proc is None:
            return
        self.proc.send(b'fin\n')
        self.post_process()

    def terminate(self):
        print('quit')
        if self.proc is None:
            return
        self.proc.send(b'quit\n')
        self.proc.terminate()
        self.proc = None
        self.bottom_widget.write("Debug process was successfully terminated.",
                                 mode='success')
        self.editor.clear_highlight_line()

    def continue_process(self):
        print('continue')
        if self.proc is None:
            return
        self.proc.send(b'c\n')
        self.post_process()

    def post_process(self):
        assert self.proc is not None
        self.proc.expect('\(gdb\)')
        msg = self.proc.before.decode()
        for line in msg.split('\r\n'):
            self.bottom_widget.write(line, mode='gdb')
        last_line = msg.split('\r\n')[-2]
        if last_line.endswith("exited normally]"):
            self.terminate()
        else:
            line_num = int(last_line.split('\t')[0])
            self.editor.highlight_current_line(line_num)



def main():
    app = QtWidgets.QApplication(sys.argv)
    main = CustomMainWindow()
    main.show()
    app.exec_()


if __name__ == '__main__':
    main()