#!/usr/bin/env python3
import codecs
import glob
import os
import shutil
import signal
import subprocess
import sys
from typing import *

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import pexpect

from rujaion import console
from rujaion import display_widget
from rujaion import editor
from rujaion.command import login, submit, test
from rujaion import util
from rujaion.util import WriteObj
from rujaion import webview_widget

# TODO: watch selected variable
# TODO: highlight multi line comment
# TODO: display tree
# TODO: highlight selecting variable
# TODO: progress bar
# TODO: rustsym(find usage)r
# TODO: highlight corresponding parenthesis


class RujaionMainWindow(QtWidgets.QMainWindow):
    test_data_dir = "./test"
    test_case_editor = "gedit"

    def __init__(self, parent=None):
        super(RujaionMainWindow, self).__init__(parent)
        self.settings = QtCore.QSettings("RustDebugger", "RustDebugger")

        self.setWindowTitle("Rujaion")
        self.setStyleSheet("background-color: white")

        # lang_box placed before add editor
        self.lang_box = QtWidgets.QComboBox(self)
        self.lang_box.addItem("rust")
        self.lang_box.addItem("c++")
        self.lang_box.addItem("python3")

        self.addCentral()

        self.file_tool = self.addToolBar("File")
        newbutton = self.file_tool.addAction("New...")
        newbutton.triggered.connect(self.newFile)

        openbutton = self.file_tool.addAction("Open...")
        openbutton.triggered.connect(self.showFileDialog)

        savebutton = self.file_tool.addAction("Save...")
        savebutton.triggered.connect(self.saveFile)

        # compilebutton = self.edit_tool.addAction("Compile...")
        # compilebutton.triggered.connect(self.compile)

        self.contest_tool = self.addToolBar("Contest")
        testbutton = self.contest_tool.addAction("Test...")
        testbutton.triggered.connect(self.testMyCode)

        debugbutton = self.contest_tool.addAction("Debug TestCase...")
        debugbutton.triggered.connect(self.debugWithTestData)

        submitbutton = self.contest_tool.addAction("Submit!...")
        submitbutton.triggered.connect(self.submit)

        self.debug_tool = self.addToolBar("Debug")
        continuebutton = self.debug_tool.addAction("Continue...")
        continuebutton.triggered.connect(self.continue_process)

        nextbutton = self.debug_tool.addAction("Next...")
        nextbutton.triggered.connect(self.next)

        stepinbutton = self.debug_tool.addAction("Step In...")
        stepinbutton.triggered.connect(self.stepIn)

        stepoutbutton = self.debug_tool.addAction("Step Out...")
        stepoutbutton.triggered.connect(self.stepOut)

        terminatebutton = self.debug_tool.addAction("Terminate...")
        terminatebutton.triggered.connect(self.terminate)

        findbutton = self.debug_tool.addAction("Find...")
        findbutton.triggered.connect(self.editor.find)

        self.config_tool = self.addToolBar("Config")
        self.config_tool.addWidget(self.lang_box)

        # Add MenuBar
        menuBar = self.menuBar()
        filemenu = menuBar.addMenu("&File")

        a = QtWidgets.QAction("New", self)
        a.triggered.connect(self.newFile)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Open", self)
        a.triggered.connect(self.showFileDialog)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Save", self)
        a.triggered.connect(self.saveFile)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Save as", self)
        a.triggered.connect(self.saveFileAs)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Clear Backup", self)
        a.triggered.connect(self.clearBackup)
        filemenu.addAction(a)

        filemenu = menuBar.addMenu("&Program")

        a = QtWidgets.QAction("Run (Ctrl+F9)", self)
        a.triggered.connect(self.run)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Debug (F9)", self)
        a.triggered.connect(self.debug)
        filemenu.addAction(a)

        filemenu = menuBar.addMenu("&Contest")

        a = QtWidgets.QAction("Login", self)
        a.triggered.connect(self.login)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Test My Code (Ctrl+F4)", self)
        a.triggered.connect(self.testMyCode)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Test With Options", self)
        a.triggered.connect(self.testMyCodeWithOptions)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Test Interactive", self)
        a.triggered.connect(self.testReactive)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Debug With Test Data (F4)", self)
        a.triggered.connect(self.debugWithTestData)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Add Test", self)
        a.triggered.connect(self.addTest)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Clear Test Data", self)
        a.triggered.connect(self.clearTestData)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Submit!", self)
        a.triggered.connect(self.submit)
        filemenu.addAction(a)

        self.debug_process = None
        try:
            self.openFile(self.settings.value("LastOpenedFile", type=str))
        except FileNotFoundError:
            pass
        self.lang_box.setCurrentText(self.editor.lang)
        self.lang_box.currentTextChanged.connect(self.editor.lang_changed)
        self.resize(self.settings.value("size", QtCore.QSize(1000, 900)))
        self.move(self.settings.value("pos", QtCore.QPoint(50, 50)))
        self.last_used_testcase = ""
        self.gdb_timeout = 4.0
        self.browser_dock = QtWidgets.QDockWidget("", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.browser_dock)
        self.addConsole()
        self.commander = util.Commander(self.console)
        self.addDisplay()
        self.addBrowser()

    def updateWindowTitle(self, running: bool = False):
        title = ""
        if self.editor.edited:
            title = "(*) "
        if self.debug_process is not None:
            title += "(Debugging...) "
        elif running:
            title += "(Running...) "
        if self.editor.fname:
            title += self.editor.fname
        else:
            title += "Scratch"
        self.setWindowTitle(title)

    def closeEvent(self, e: QtGui.QKeyEvent):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if (
            event.modifiers() == QtCore.Qt.ShiftModifier
            and event.key() == QtCore.Qt.Key_F8
        ):
            self.stepOut()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_F9
        ):
            self.run()
        elif event.key() == QtCore.Qt.Key_F9:
            self.debug()
        elif event.key() == QtCore.Qt.Key_F8:
            self.next()
        elif event.key() == QtCore.Qt.Key_F7:
            self.stepIn()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_F4
        ):
            self.testMyCode()
        elif event.key() == QtCore.Qt.Key_F4:
            self.debugWithLastCase()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_F6
        ):
            self.submit()
        elif event.key() == QtCore.Qt.Key_F6:
            self.browser_widget.focusOnUrlEdit()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_F12
        ):
            if self.debug_process is not None:
                return

            if self.editor.isHidden():
                self.editor.show()
                self.console.show()
                self.browser_dock.hide()
            else:
                self.editor.hide()
                self.console.hide()
                self.browser_dock.show()
                self.editor.setFocus()
        elif event.key() == QtCore.Qt.Key_F12:
            if self.editor.isHidden():
                self.editor.show()
                self.console.show()
                self.browser_widget.browser.setFocus()
            if self.browser_dock.isHidden():
                self.browser_dock.show()
            else:
                self.browser_dock.hide()
        elif event.key() == QtCore.Qt.Key_F11:
            if self.console_dock.isHidden():
                self.console_dock.show()
            else:
                self.console_dock.hide()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.terminate()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_O
        ):
            self.showFileDialog()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_S
        ):
            self.saveFile()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_W
        ):
            self.saveFileAs()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_F
        ):
            self.editor.find()
        elif (
            event.modifiers() == QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_N
        ):
            self.newFile()
        else:
            event.accept()

    def showFileDialog(self):
        dirname = os.path.dirname(self.settings.value("LastOpenedFile", type=str))
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open", dirname, "Source Files (*.rs *.cpp *.cc *.py *.bak)"
        )[0]
        self.openFile(fname)

    def openFile(self, fname: str):
        if not fname:
            return
        self.editor.open_file(fname)
        self.settings.setValue("LastOpenedFile", fname)
        self.updateWindowTitle()

    def clearBackup(self):
        if not self.editor.fname:
            return
        for fname in glob.glob(os.path.dirname(self.editor.fname) + "/*.bak"):
            os.remove(fname)

    def askTerminateOrNot(self) -> bool:
        ret = QtWidgets.QMessageBox.information(
            None,
            "Debugging process is runnning",
            "Do you want to terminate debug process" " and start new process?",
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No,
        )

        if ret == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def saveFileAs(self):
        if self.editor.fname:
            default_dir = os.path.dirname(self.editor.fname)
        else:
            default_dir = os.path.dirname(
                self.settings.value("LastOpenedFile", type=str)
            )
        default_file_name = os.path.join(default_dir, self.editor.default_file_name())
        savename = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save file", default_file_name, "Source Files (*.rs *.cpp)"
        )[0]
        if not savename:
            return
        self.editor.save_pre_process()
        with codecs.open(savename, "w", "utf-8") as f:
            f.write(self.editor.toPlainText())
        self.editor.fname = savename
        self.editor.reset_lang()
        self.savePostProcess()
        self.settings.setValue("LastOpenedFile", savename)

    def savePostProcess(self):
        self.updateWindowTitle()
        self.compile()

    def saveFile(self):
        if self.editor.fname:
            if self.editor.edited and os.path.exists(self.editor.fname):
                for i in range(50):
                    backup_name = self.editor.fname + "." + str(i) + ".bak"
                    if not os.path.exists(backup_name):
                        shutil.copy(self.editor.fname, backup_name)
                        break
            self.editor.save_pre_process()
            with codecs.open(self.editor.fname, "w", "utf-8") as f:
                f.write(self.editor.toPlainText())
            self.savePostProcess()
        else:
            self.saveFileAs()

    def addEditer(self, parent):
        self.editor = editor.Editter(parent)
        self.editor.toggleBreakSignal.connect(self.UpdateBreak)
        self.edited = False
        self.editor.textChanged.connect(self.updateWindowTitle)

    def addCentral(self):
        self.addEditer(self)
        self.setCentralWidget(self.editor)

    def addDisplay(self):
        self.display_widget = display_widget.ResultTableModel(self)
        self.browser_dock.setWidget(self.display_widget)
        self.display_widget.cellChanged.connect(self.processDisplayEdited)

    def addBrowser(self):
        self.browser_widget = webview_widget.WebViewWindow(self)
        self.browser_dock.setWidget(self.browser_widget)
        url = self.settings.value("contest url", "")
        self.browser_widget.changePage(url)

    def processDisplayEdited(self, row_num, column_num):
        if self.debug_process is not None:
            self.display_one_valuable(row_num)

    def addConsole(self):
        self.console = console.Console(self)
        self.console_dock = QtWidgets.QDockWidget("Console", self)
        self.console_dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

    def newFile(self):
        if self.lang_box.currentText() == "rust":
            self.editor.new_file(os.path.join(util.get_resources_dir(), "template.rs"))
        elif self.lang_box.currentText() == "c++":
            self.editor.new_file(os.path.join(util.get_resources_dir(), "template.cpp"))
        else:
            self.editor.new_file(os.path.join(util.get_resources_dir(), "template.py"))

    def compile(self, no_debug: bool = False):
        self.console.clear()
        self.editor.reset_compile_info()
        if not self.editor.fname:
            util.disp_error("File is not opened.")
        command = util.compile_command(self.editor.lang, no_debug) + [self.editor.fname]
        try:
            out = subprocess.check_output(command, stderr=subprocess.STDOUT)
            self.console.writeLnSignal.emit("[+] Compile is finished successfully!")
            error_places, warning_places = self.parse_compile_error(out.decode())
            self.editor.highlight_compile_error(warning_places, is_warning=True)
        except subprocess.CalledProcessError as err:
            self.console.writeSignal.emit(WriteObj(err.output, mode="error"))
            error_places, warning_places = self.parse_compile_error(err.output.decode())
            self.editor.highlight_compile_error(error_places, is_warning=False)
            return False
        return True

    def is_error_disp_line(self, lines: List[str], i: int):
        if self.editor.lang == "rust":
            if i == 0:
                return False
            return lines[i - 1].startswith("error") and "-->" in lines[i]
        elif self.editor.lang == "c++":
            return ": error:" in lines[i]
        else:
            return "error" in lines[i]

    def is_warning_disp_line(self, lines: List[str], i: int):
        if self.editor.lang == "rust":
            if i == 0:
                return False
            return lines[i - 1].startswith("warning") and "-->" in lines[i]
        else:
            return ": warning:" in lines[i]

    def parse_compile_error(self, error_message: str):
        error_disp_lines = []
        warning_disp_lines = []
        lines = error_message.split("\n")
        for i, line in enumerate(lines):
            if self.is_error_disp_line(lines, i):
                error_disp_lines.append(i)
            elif self.is_warning_disp_line(lines, i):
                warning_disp_lines.append(i)

        error_places = []
        for num in error_disp_lines:
            invalid_line, invalid_pos = lines[num].split(":")[1:3]
            try:
                error_places.append((int(invalid_line), int(invalid_pos)))
            except ValueError:
                pass

        warning_places = []
        for num in warning_disp_lines:
            invalid_line, invalid_pos = lines[num].split(":")[1:3]
            try:
                warning_places.append((int(invalid_line), int(invalid_pos)))
            except ValueError:
                pass

        return error_places, warning_places

    def run(self):
        if self.debug_process is not None:
            if self.askTerminateOrNot():
                self.terminate()
            else:
                return
        if not self.compile(no_debug=True):
            return
        self.updateWindowTitle(True)
        compiled_file = util.get_compiled_file(self.editor.lang, self.editor.fname)
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not found.")
        try:
            output = subprocess.check_output(
                util.exec_command(self.editor.lang) + [compiled_file],
                stderr=subprocess.STDOUT,
            )
            self.console.writeLnSignal.emit(output)
        except subprocess.CalledProcessError as err:
            self.console.writeLnSignal.emit("[-] " + err.output.decode())
            self.console.writeLnSignal.emit("[-] Run process is terminated abnormally.")
            self.updateWindowTitle(False)
            return
        self.console.writeLnSignal.emit("[+] Run process is finished successfully!")
        self.updateWindowTitle(False)

    def with_debug_display(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if self.debug_process is not None:
                self.browser_dock.show()
                self.browser_dock.setWidget(self.display_widget)

        return wrapper

    def with_console(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if self.debug_process is not None:
                self.console_dock.show()

        return wrapper

    @with_debug_display
    @with_console
    def debug(self, *args, **kwargs):
        self.console.clear()
        if not self.compile():
            return
        if self.debug_process is not None:
            if self.askTerminateOrNot():
                self.terminate()
            else:
                return
        compiled_file = util.get_compiled_file(self.editor.lang, self.editor.fname)
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not found.")
        try:
            assert self.debug_process is None
            self.debug_process = pexpect.spawn(
                util.debug_command(self.editor.lang) + " " + compiled_file
            )
            util.wait_input_ready(self.debug_process, self.editor.lang)
            self.console.writeSignal.emit(WriteObj(self.debug_process.before.decode()))

            for com in self.editor.generateBreak():
                self.debug_process.send(com)
                util.wait_input_ready(self.debug_process, self.editor.lang)
                self.console.writeSignal.emit(
                    WriteObj(self.debug_process.before.decode(), mode="gdb")
                )

            print("run " + compiled_file)
            self.debug_process.send(b"run\n")
            self.updateWindowTitle()
            if self.editor.lang == "python3":
                util.wait_input_ready(self.debug_process, self.editor.lang)
                self.debug_process.send(b"continue\n")
            self.post_process()

        except subprocess.CalledProcessError as err:
            self.console.writeSignal(WriteObj(err, mode="error"))

    def debugWithLastCase(self):
        self.debugWithTestData(True)

    @with_debug_display
    @with_console
    def debugWithTestData(self, use_lastcase=False):
        self.console.clear()
        if not self.compile():
            return
        if self.debug_process is not None:
            if self.askTerminateOrNot():
                self.terminate()
            else:
                return
        if (
            use_lastcase
            and self.last_used_testcase
            and os.path.isfile(self.last_used_testcase)
        ):
            fname = self.last_used_testcase
        else:
            fname = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open", self.test_data_dir, "Test data (*.in)"
            )[0]
        if not fname:
            self.last_used_testcase = ""
            return
        self.last_used_testcase = fname

        with open(fname) as fr:
            inputs = [line for line in fr if line]

        compiled_file = util.get_compiled_file(self.editor.lang, self.editor.fname)
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not found.")
        try:
            if self.debug_process is None:
                self.debug_process = pexpect.spawn(
                    util.debug_command(self.editor.lang) + " " + compiled_file
                )
                self.console.terminate_evcxr()
            else:
                self.continue_process()
                return
            util.wait_input_ready(self.debug_process, self.editor.lang)
            for com in self.editor.generateBreak():
                self.debug_process.send(com)
                util.wait_input_ready(self.debug_process, self.editor.lang)
                self.console.writeSignal.emit(
                    WriteObj(self.debug_process.before.decode(), mode="gdb")
                )

            print("run " + compiled_file)
            self.debug_process.send(b"run\n")
            self.updateWindowTitle()
            if self.editor.lang == "python3":
                util.wait_input_ready(self.debug_process, self.editor.lang)
                self.debug_process.send(b"continue\n")
            for i, debug_input in enumerate(inputs):
                msg = self.debug_process.before.decode()
                for line in msg.split("\r\n"):
                    self.console.writeSignal.emit(WriteObj(line, mode="gdb"))

                for line in reversed(msg.split("\r\n")):
                    if line.endswith("exited normally]"):
                        if i != len(inputs) - 1:
                            self.console.writeLnSignal.emit(
                                "[-] Partial input is rejected"
                            )
                        self.terminate()
                        return
                    if "exited with code" in line:
                        self.console.writeLnSignal.emit(
                            "[-] Process is finished with error"
                        )
                        self.terminate()
                        return

                self.debug_process.send(debug_input.encode())
            self.post_process()
            self.updateWindowTitle()
            self.console.run_evcxr()

        except subprocess.CalledProcessError as err:
            self.console.writeSignal.emit(WriteObj(err, mode="error"))
            self.console.run_evcxr()

    def addTest(self):
        if not os.path.exists(self.test_data_dir):
            os.mkdir(self.test_data_dir)
        test_data_files = set(os.listdir(self.test_data_dir))
        for i in range(1, 100):
            if not "sample-{}.in".format(i) in test_data_files:
                in_file = os.path.join(self.test_data_dir, "sample-{}.in".format(i))
                out_file = os.path.join(self.test_data_dir, "sample-{}.out".format(i))
                subprocess.Popen(
                    ("gedit", in_file, out_file),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                break

    def UpdateBreak(self, command: bytes):
        if self.debug_process is None:
            return
        if command.startswith(b"b "):
            self.debug_process.send(command)
            util.wait_input_ready(self.debug_process, self.editor.lang)
        else:
            self.debug_process.send("i b\n".encode())
            util.wait_input_ready(self.debug_process, self.editor.lang)
            print(self.debug_process.before.decode())
            last_num = -1
            for line in self.debug_process.before.decode().split("\r\n"):
                if line.split(" ")[0].isdecimal():
                    last_num = int(line.split(" ")[0])
                if line.rstrip("\n").endswith(":" + command.decode()):
                    assert last_num != -1
                    self.debug_process.send(("d " + str(last_num) + "\n").encode())
                    util.wait_input_ready(self.debug_process, self.editor.lang)
                    break

    def next(self):
        print("next")
        if self.debug_process is None:
            return
        self.debug_process.send(b"n\n")
        self.post_process()

    def stepIn(self):
        print("step in")
        if self.debug_process is None:
            return
        self.debug_process.send(b"s\n")
        self.post_process()

    def stepOut(self):
        print("step out")
        if self.debug_process is None:
            return
        self.debug_process.send(b"fin\n")
        self.post_process()

    def terminate(self):
        print("quit")
        if self.debug_process is None:
            return
        self.debug_process.send(b"quit\n")
        self.debug_process.terminate()
        self.debug_process = None
        self.console.writeLnSignal.emit(
            "[+] Debug process was successfully terminated."
        )
        self.editor.clear_highlight_line()
        self.updateWindowTitle()
        self.browser_dock.setWidget(self.browser_widget)

    def continue_process(self):
        print("continue")
        if self.debug_process is None:
            return
        self.debug_process.send(b"c\n")
        self.post_process()

    def post_process(self):
        assert self.debug_process is not None
        try:
            util.wait_input_ready(
                self.debug_process, self.editor.lang, self.gdb_timeout
            )
        except:
            print(str(self.debug_process))
            self.console.writeLnSignal.emit("[-] Debug process is timeout")
            self.terminate()
            return
        msg = self.debug_process.before.decode()
        for line in msg.split("\r\n"):
            self.console.writeSignal.emit(WriteObj(line, mode="gdb"))

        for line in reversed(msg.split("\r\n")):
            if line.endswith("exited normally]") or line.startswith(
                "The program finished"
            ):
                self.terminate()
                return
            elif line.endswith("No such file or directory.") or line.endswith(
                "そのようなファイルやディレクトリはありません."
            ):
                self.stepOut()
                return
            elif "exited with code" in line:
                self.console.writeLnSignal.emit("[-] Process is finished with error")
                self.terminate()
                return
            else:
                line_num = util.get_executing_line(self.editor.lang, line)
                if line_num is None:
                    continue
                self.editor.highlight_executing_line(line_num)
                self.editor.repaint()
                break

        for i, _ in self.display_widget.name_iter():
            self.display_one_valuable(i)

    def display_one_valuable(self, row_num: int):
        # Avoid infinity loop
        self.display_widget.cellChanged.disconnect(self.processDisplayEdited)

        name = self.display_widget.item(row_num, 0).text()
        if not name:
            self.display_widget.set_cell(row_num, 1, "")
            self.display_widget.set_cell(row_num, 2, "")
            self.display_widget.cellChanged.connect(self.processDisplayEdited)
            return
        self.debug_process.send(b"p " + name.encode() + b"\n")
        util.wait_input_ready(self.debug_process, self.editor.lang)
        value = "".join(self.debug_process.before.decode().split("\r\n")[1:])
        value = value.split(" = ")[-1]
        # value = ''.join(value.split(' = ')[1:])
        self.display_widget.set_cell(row_num, 1, value)

        if self.editor.lang == "python3":
            self.debug_process.send(b"whatis " + name.encode() + b"\n")
        else:
            self.debug_process.send(b"pt " + name.encode() + b"\n")
        util.wait_input_ready(self.debug_process, self.editor.lang)
        type = "".join(self.debug_process.before.decode().split("\n")[1:])
        type = type.split(" = ")[-1]
        type = type.split(" {")[0]
        self.display_widget.set_cell(row_num, 2, type)

        self.display_widget.cellChanged.connect(self.processDisplayEdited)

    @with_console
    def download(self, url: str = None):
        self.settings.setValue("contest url", url)
        self.clearTestData()
        self.commander.cmd = ("oj", "download", url)
        self.commander.start()
        # self.console.writeLnSignal.emit("[+] Downloaded Test data")

    def login(self):
        login.LoginDialog(
            self,
            url=self.browser_widget.browser.url().toString(),
            settings=self.settings,
        ).show()

    def clearTestData(self):
        if os.path.isdir(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def exists_float_output(self) -> bool:
        """ If "." character found in any *.out file, return True.
        """
        try:
            subprocess.check_output(
                "grep -F . {}/*.out".format(self.test_data_dir), shell=True
            )
        except subprocess.CalledProcessError:
            return False
        return True

    @with_console
    def testMyCode(self, *args):
        self.console.clear()
        if not self.compile(no_debug=True):
            return
        compiled_file = util.get_compiled_file(self.editor.lang, self.editor.fname)
        test_command = "{}".format(
            " ".join(util.exec_command(self.editor.lang) + [compiled_file])
        )
        try:
            command = ["oj", "test", "-c", test_command]
            print(command)
            if self.exists_float_output():
                error = 0.00000001
                command += ["-e", str(error)]
                self.console.writeLnSignal.emit("[.] Found float expectation")
                self.console.writeLnSignal.emit("[.] Allow {} error".format(error))
            # TODO: configurable timeout
            out = subprocess.check_output(
                command, stderr=subprocess.STDOUT, timeout=4.0
            ).decode()
            self.console.writeLnSignal.emit(out)
        except subprocess.TimeoutExpired as e:
            self.console.writeLnSignal.emit(e.output)
            self.console.writeLnSignal.emit("[-] Test is Timeout")
            return
        except subprocess.CalledProcessError as e:
            self.console.writeLnSignal.emit(e.output)
        except Exception as e:
            self.console.writeSignal.emit(WriteObj(e, mode="error"))
            return

    @with_console
    def testMyCodeWithOptions(self, *args):
        self.console.clear()
        if not self.compile(no_debug=True):
            return
        compiled_file = util.get_compiled_file(self.editor.lang, self.editor.fname)
        test.TestDialog(
            self, compiled_file=compiled_file, settings=self.settings
        ).show()

    @with_console
    def testReactive(self, *args):
        self.console.clear()
        if not self.compile(no_debug=True):
            return
        compiled_file = util.get_compiled_file(self.editor.lang, self.editor.fname)
        test.TestReactiveDialog(
            self, compiled_file=compiled_file, settings=self.settings
        ).show()

    @with_console
    def submit(self, *args):
        if not self.editor.fname:
            util.disp_error("Please save this file")
        submit.SubmitDialog(
            self,
            url=self.browser_widget.browser.url().toString(),
            lang=self.editor.lang_as_option(),
            settings=self.settings,
        ).show()


app = QtWidgets.QApplication(sys.argv)


def handler(signum, frame):
    util.OJ_MUTEX.lock()
    print("shutdown with signal={}".format(signum))
    global app
    app.exit(0)


def main():
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "../img/icon.png"
    )
    app.setWindowIcon(QIcon(icon_path))
    main = RujaionMainWindow()
    main.show()
    app.exec_()


if __name__ == "__main__":
    main()
    import http.cookiejar
