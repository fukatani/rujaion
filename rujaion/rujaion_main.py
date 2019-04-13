import codecs
import os
import shutil
import subprocess
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import pexpect

from rujaion import display_widget
from rujaion import syntax
from rujaion import editor
from rujaion import login
from rujaion import util
from rujaion import console

# TODO: watch selected variable
# TODO: highlight multi line comment
# TODO: display dp
# TODO: refactoring
# TODO: display tree
# TODO: highlight selecting variable
# TODO: fix gdb hang (std)
# TODO: progress bar
# TODO: rustsym(find usage)r
# TODO: highlight corresponding parenthesis


class RujaionMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(RujaionMainWindow, self).__init__(parent)

        self.setWindowTitle("RustGUIDebugger")
        self.setStyleSheet("background-color: white")
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

        a = QtWidgets.QAction("Download (F6)", self)
        a.triggered.connect(self.download)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Test My Code (Ctrl+F4)", self)
        a.triggered.connect(self.testMyCode)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Debug With Test Data (F4)", self)
        a.triggered.connect(self.debugWithTestData)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Clear Test Data", self)
        a.triggered.connect(self.clearTestData)
        filemenu.addAction(a)

        a = QtWidgets.QAction("Submit!", self)
        a.triggered.connect(self.submit)
        filemenu.addAction(a)

        self.proc = None
        self.settings = QtCore.QSettings("RustDebugger", "RustDebugger")
        try:
            self.openFile(self.settings.value("LastOpenedFile", type=str))
        except FileNotFoundError:
            pass
        self.resize(self.settings.value("size", QtCore.QSize(1000, 900)))
        self.move(self.settings.value("pos", QtCore.QPoint(50, 50)))
        self.addConsole()
        self.addDisplay()
        self.last_used_testcase = ""

    def updateWindowTitle(self, running=False):
        title = ""
        if self.editor.edited:
            title = "(*) "
        if self.proc is not None:
            title += "(Debugging...) "
        elif running:
            title += "(Running...) "
        if self.editor.fname:
            title += self.editor.fname
        else:
            title += "Scratch"

        self.setWindowTitle(title)

    def closeEvent(self, e):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()

    def keyPressEvent(self, event):
        if (
            event.modifiers()
            and QtCore.Qt.ShiftModifier
            and event.key == QtCore.Qt.Key_F8
        ):
            self.stepOut()
        elif (
            event.modifiers()
            and QtCore.Qt.ControlModifier
            and event.key == QtCore.Qt.Key_F9
        ):
            self.run()
        elif event.key() == QtCore.Qt.Key_F9:
            self.debug()
        elif event.key() == QtCore.Qt.Key_F8:
            self.next()
        elif event.key() == QtCore.Qt.Key_F7:
            self.stepIn()
        elif event.key() == QtCore.Qt.Key_F5:
            self.reflesh()
        elif event.key() == QtCore.Qt.Key_F2:
            self.jump()
        elif (
            event.modifiers()
            and QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_F4
        ):
            self.testMyCode()
        elif event.key() == QtCore.Qt.Key_F4:
            self.debugWithLastCase()
        elif event.key() == QtCore.Qt.Key_F6:
            self.download()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.terminate()
        elif (
            event.modifiers()
            and QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_O
        ):
            self.showFileDialog()
        elif (
            event.modifiers()
            and QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_S
        ):
            self.saveFile()
        elif (
            event.modifiers()
            and QtCore.Qt.ControlModifier
            and event.key() == QtCore.Qt.Key_W
        ):
            self.saveFileAs()
        else:
            event.accept()

    def showFileDialog(self):
        dirname = os.path.dirname(self.settings.value("LastOpenedFile", type=str))
        fname = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open", dirname, "Rust Files (*.rs)"
        )[0]
        self.openFile(fname)

    def openFile(self, fname):
        if not fname:
            return
        self.editor.open_file(fname)
        self.settings.setValue("LastOpenedFile", fname)
        self.updateWindowTitle()

    def askTerminateOrNot(self):
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

    def reflesh(self):
        if not self.editor.fname:
            return
        cursor = self.editor.textCursor()
        line_num = cursor.blockNumber()
        char_num = cursor.columnNumber()
        self.editor.open_file(self.editor.fname)
        cursor = QtGui.QTextCursor(
            self.editor.document().findBlockByLineNumber(line_num)
        )
        cursor.movePosition(
            QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.MoveAnchor, char_num
        )
        self.editor.setTextCursor(cursor)

    def saveFileAs(self):
        savename = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "")[0]
        if not savename:
            return
        fname = codecs.open(savename, "w", "utf-8")
        fname.write(self.editor.toPlainText())
        fname.close()
        self.editor.fname = savename
        self.editor.edited = False
        self.updateWindowTitle()
        self.compile()

    def saveFile(self):
        if self.editor.fname:
            scroll_value = self.editor.verticalScrollBar().value()
            f = codecs.open(self.editor.fname, "w", "utf-8")
            f.write(self.editor.toPlainText())
            f.close()
            try:
                out = subprocess.check_output(
                    "rustfmt " + self.editor.fname, shell=True, stderr=subprocess.STDOUT
                )
            except Exception as err:
                self.console.write(err.output)
            self.reflesh()
            self.editor.edited = False
            self.editor.verticalScrollBar().setValue(scroll_value)
            self.editor.repaint()
            self.editor.highlight_cursor_line()
            self.updateWindowTitle()
            self.compile()
        else:
            self.saveFileAs()

    def addEditer(self, parent):
        self.editor = editor.RustEditter(parent)
        self.highlighter = syntax.RustHighlighter(self.editor.document())
        self.editor.toggleBreakSignal.connect(self.UpdateBreak)
        self.edited = False
        self.editor.textChanged.connect(self.updateWindowTitle)

    def addCentral(self):
        self.addEditer(self)
        self.setCentralWidget(self.editor)

    def addDisplay(self):
        self.display_widget = display_widget.ResultTableModel(self)
        dock = QtWidgets.QDockWidget("Display", self)
        dock.setWidget(self.display_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.display_widget.cellChanged.connect(self.processDisplayEdited)

    def processDisplayEdited(self, row_num, column_num):
        if self.proc is not None:
            self.display_one_valuable(row_num)

    def addConsole(self):
        self.console = console.Console(self)
        dock = QtWidgets.QDockWidget("Console", self)
        dock.setWidget(self.console)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def newFile(self):
        self.editor.new_file(os.path.join(os.path.dirname(__file__), "template.rs"))

    def compile(self, no_debug=False):
        self.console.clear()
        if not self.editor.fname:
            util.disp_error("File is not opened.")
        if no_debug:
            command = ("rustc", self.editor.fname)
        else:
            command = ("rustc", "-g", self.editor.fname)
        try:
            out = subprocess.check_output(command, stderr=subprocess.STDOUT)
            self.console.write("Compile is finished successfully!", mode="success")
            error_places, warning_places = self.parse_compile_error(out.decode())
            self.editor.highlight_compile_error(error_places, warning_places)
        except subprocess.CalledProcessError as err:
            self.console.write(err.output, mode="error")
            error_places, warning_places = self.parse_compile_error(err.output.decode())
            self.editor.highlight_compile_error(error_places, warning_places)
            return False
        return True

    def parse_compile_error(self, error_message):
        error_disp_lines = []
        warning_disp_lines = []
        lines = error_message.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("error") and "-->" in lines[i + 1]:
                error_disp_lines.append(i + 1)
            elif line.startswith("warning") and "-->" in lines[i + 1]:
                warning_disp_lines.append(i + 1)

        error_places = []
        for num in error_disp_lines:
            invalid_line, invalid_pos = lines[num].split(":")[1:]
            error_places.append((int(invalid_line), int(invalid_pos)))

        warning_places = []
        for num in warning_disp_lines:
            invalid_line, invalid_pos = lines[num].split(":")[1:]
            warning_places.append((int(invalid_line), int(invalid_pos)))

        return error_places, warning_places

    def run(self):
        if self.proc is not None:
            if self.askTerminateOrNot():
                self.terminate()
            else:
                return
        if not self.compile(no_debug=True):
            return
        self.updateWindowTitle(True)
        compiled_file = os.path.basename(self.editor.fname).replace(".rs", "")
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not opened.")
        try:
            output = subprocess.check_output(
                ("env", "RUST_BACKTRACE=1", "./" + compiled_file),
                stderr=subprocess.STDOUT,
            )
            self.console.write(output)
        except subprocess.CalledProcessError as err:
            self.console.write(err.output, mode="error")
        self.console.write("Run process is finished successfully!", mode="success")
        self.updateWindowTitle(False)

    def debug(self):
        self.console.clear()
        if not self.compile():
            return
        if self.proc is not None:
            if self.askTerminateOrNot():
                self.terminate()
            else:
                return
        compiled_file = os.path.basename(self.editor.fname).replace(".rs", "")
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not opened.")
        try:
            assert self.proc is None
            self.proc = pexpect.spawn(
                "env RUST_BACKTRACE=1 rust-gdb  ./" + compiled_file
            )
            self.proc.expect("\(gdb\)")
            self.console.write(self.proc.before.decode())

            for com in self.editor.generateBreak():
                self.proc.send(com)
                self.proc.expect("\(gdb\)")
                self.console.write(self.proc.before.decode(), mode="gdb")

            print("run " + compiled_file)
            self.proc.send(b"run\n")
            self.updateWindowTitle()
            self.post_process()

        except subprocess.CalledProcessError as err:
            self.console.write(err, mode="error")

    def debugWithLastCase(self):
        self.debugWithTestData(True)

    def debugWithTestData(self, use_lastcase=False):
        self.console.clear()
        if not self.compile():
            return
        if self.proc is not None:
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
                self, "Open", "./test", "Test data (*.in)"
            )[0]
        if not fname:
            self.last_used_testcase = ""
            return
        self.last_used_testcase = fname

        with open(fname) as fr:
            inputs = [line for line in fr if line]

        compiled_file = os.path.basename(self.editor.fname).replace(".rs", "")
        if not os.path.isfile(compiled_file):
            util.disp_error("Compiled file is not opened.")
        try:
            if self.proc is None:
                self.proc = pexpect.spawn(
                    "env RUST_BACKTRACE=1 rust-gdb  ./" + compiled_file
                )
                self.console.terminate_evcxr()
            else:
                self.continue_process()
                return
            self.proc.expect("\(gdb\)")
            for com in self.editor.generateBreak():
                self.proc.send(com)
                self.proc.expect("\(gdb\)")
                self.console.write(self.proc.before.decode(), mode="gdb")

            print("run " + compiled_file)
            self.proc.send(b"run\n")
            self.updateWindowTitle()
            for i, debug_input in enumerate(inputs):
                try:
                    self.proc.expect("\(gdb\)", timeout=0.5)
                except:
                    pass
                msg = self.proc.before.decode()
                for line in msg.split("\r\n"):
                    self.console.write(line, mode="gdb")

                for line in reversed(msg.split("\r\n")):
                    if line.endswith("exited normally]"):
                        if i != len(inputs) - 1:
                            self.console.write(
                                "Partial input is rejected", mode="error"
                            )
                        self.terminate()
                        return
                    if "exited with code" in line:
                        self.console.write(
                            "Process is finished with error", mode="error"
                        )
                        self.terminate()
                        return

                self.proc.send(debug_input.encode())
            self.post_process()
            self.console.run_evcxr()

        except subprocess.CalledProcessError as err:
            self.console.write(err, mode="error")
            self.console.run_evcxr()

    def UpdateBreak(self, command):
        if self.proc is None:
            return
        if command.startswith(b"b "):
            self.proc.send(command)
            self.proc.expect("\(gdb\)")
        else:
            self.proc.send("i b\n".encode())
            self.proc.expect("\(gdb\)")
            print(self.proc.before.decode())
            last_num = -1
            for line in self.proc.before.decode().split("\r\n"):
                if line.split(" ")[0].isdecimal():
                    last_num = int(line.split(" ")[0])
                if line.rstrip("\n").endswith(":" + command.decode()):
                    assert last_num != -1
                    self.proc.send(("d " + str(last_num) + "\n").encode())
                    self.proc.expect("\(gdb\)")
                    break

    def next(self):
        print("next")
        if self.proc is None:
            return
        self.proc.send(b"n\n")
        self.post_process()

    def stepIn(self):
        print("step in")
        if self.proc is None:
            return
        self.proc.send(b"s\n")
        self.post_process()

    def stepOut(self):
        print("step out")
        if self.proc is None:
            return
        self.proc.send(b"fin\n")
        self.post_process()

    def terminate(self):
        print("quit")
        if self.proc is None:
            return
        self.proc.send(b"quit\n")
        self.proc.terminate()
        self.proc = None
        self.console.write("Debug process was successfully terminated.", mode="success")
        self.editor.clear_highlight_line()
        self.updateWindowTitle()

    def continue_process(self):
        print("continue")
        if self.proc is None:
            return
        self.proc.send(b"c\n")
        self.post_process()

    def post_process(self):
        assert self.proc is not None
        try:
            self.proc.expect("\(gdb\)", timeout=3)
        except:
            print(str(self.proc))
        msg = self.proc.before.decode()
        for line in msg.split("\r\n"):
            self.console.write(line, mode="gdb")

        for line in reversed(msg.split("\r\n")):
            if line.endswith("exited normally]"):
                self.terminate()
                return
            elif line.endswith("No such file or directory."):
                self.stepOut()
                return
            elif "exited with code" in line:
                self.console.write("Process is finished with error", mode="error")
                self.terminate()
                return
            else:
                try:
                    line_num = int(line.split("\t")[0])
                except ValueError:
                    continue
                self.editor.repaint()
                self.editor.highlight_executing_line(line_num)

        for i, _ in self.display_widget.name_iter():
            self.display_one_valuable(i)

    def display_one_valuable(self, row_num):
        # Avoid infinity loop
        self.display_widget.cellChanged.disconnect(self.processDisplayEdited)

        name = self.display_widget.item(row_num, 0).text()
        if not name:
            self.display_widget.set_cell(row_num, 1, "")
            self.display_widget.set_cell(row_num, 2, "")
            self.display_widget.cellChanged.connect(self.processDisplayEdited)
            return
        self.proc.send(b"p " + name.encode() + b"\n")
        self.proc.expect("\(gdb\)")
        value = "".join(self.proc.before.decode().split("\r\n")[1:])
        value = value.split(" = ")[-1]
        # value = ''.join(value.split(' = ')[1:])
        self.display_widget.set_cell(row_num, 2, value)

        self.proc.send(b"pt " + name.encode() + b"\n")
        self.proc.expect("\(gdb\)")
        type = "".join(self.proc.before.decode().split("\n")[1:])
        type = type.split(" = ")[-1]
        type = type.split(" {")[0]
        self.display_widget.set_cell(row_num, 1, type)

        self.display_widget.cellChanged.connect(self.processDisplayEdited)

    def jump(self):
        self.editor.jump()

    def download(self):
        text = self.settings.value(
            "contest url", "https://abc103.contest.atcoder.jp/tasks/abc103_b"
        )
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Download Testcases", "Contest task URL:", text=text
        )
        self.settings.setValue("contest url", text)
        if not ok:
            return

        try:
            self.clearTestData()
            out = subprocess.check_output(
                ("oj", "download", text), stderr=subprocess.STDOUT
            ).decode()
        except Exception as err:
            self.console.write(err.output)
            return
        self.console.write(out)
        self.console.write("Downloaded Test data", mode="success")

    def login(self):
        login.LoginDialog(self, settings=self.settings).show()

    def clearTestData(self):
        test_data_dir = "./test"
        if os.path.isdir(test_data_dir):
            shutil.rmtree(test_data_dir)

    def testMyCode(self):
        self.console.clear()
        if not self.compile(no_debug=True):
            return
        compiled_file = os.path.basename(self.editor.fname).replace(".rs", "")
        try:
            # TODO: configurable timeout
            out = subprocess.check_output(
                ("oj", "test", "-c", "./" + compiled_file),
                stderr=subprocess.STDOUT,
                timeout=4.0,
            ).decode()
        except subprocess.TimeoutExpired as e:
            self.console.test_result_write(e.output)
            self.console.test_result_write("[-] Test is Timeout")
            return
        except Exception as e:
            self.console.test_result_write(e.output)
            return
        self.console.test_result_write(out)

    def submit(self):
        text = self.settings.value(
            "contest url", "https://abc103.contest.atcoder.jp/tasks/abc103_b"
        )
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Submit program", "Contest task URL:", text=text
        )
        if not ok:
            return
        self.settings.setValue("contest url", text)
        if not self.editor.fname:
            util.disp_error("Please save this file")
        cmd = ("oj", "s", "-l", "rust", "-y", text, self.editor.fname)
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
        except Exception as err:
            self.console.write(err.output)
            return
        self.console.write(out)
        self.console.write("submitted", mode="success")


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = RujaionMainWindow()
    main.show()
    app.exec_()


if __name__ == "__main__":
    main()
