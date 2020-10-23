import subprocess

from PyQt5 import QtWidgets

from rujaion import util


class TestDialog(QtWidgets.QDialog):
    def __init__(self, *args, compiled_file: str, settings):
        super().__init__(*args)
        self.console = self.parent().console
        self.compiled_file = compiled_file
        # self.is_interactive = util.StateFullCheckBox(settings, "TEST_INTERACTIVE", self)
        self.tle_edit = util.StateFullTextEdit(settings, "TEST_TLE", self, "2.0")
        self.mle_edit = util.StateFullTextEdit(settings, "TEST_MLE", self, "1024")
        self.float_error_edit = util.StateFullTextEdit(
            settings, "TEST_FLOAT_ERROR", self
        )
        self.dialogs = (
            ("Submit...", None),
            ("TLE", self.tle_edit),
            ("MLE", self.mle_edit),
            ("FLOAT ERROR", self.float_error_edit),
        )
        self.draw()

    def draw(self, *args):
        main_layout = QtWidgets.QVBoxLayout()
        for name, widget in self.dialogs:
            if not widget:
                l_widget = QtWidgets.QGroupBox(name)
                l_widget.setStyleSheet(
                    """
                QGroupBox {
                    color: white;
                    border: 1px solid gray;
                    border-radius: 9px;
                    margin-top: 0.5em;
                }
                QGroupBox::title {
                    color: white;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                """
                )
                l_widget.setFlat(False)
                section_layout = QtWidgets.QFormLayout()
                l_widget.setLayout(section_layout)
                main_layout.addWidget(l_widget)
            else:
                section_layout.addRow(name, widget)
        test_button = QtWidgets.QPushButton("Test")
        test_button.clicked.connect(self.test)
        main_layout.addWidget(test_button)
        self.setLayout(main_layout)

    def test(self):
        for name, widget in self.dialogs:
            try:
                widget.commit()
            except AttributeError:
                pass
        try:
            command = ["oj", "test", "-c", self.compiled_file]
            if self.float_error_edit.text():
                command += ["-e", str(self.float_error_edit.text())]
            if self.tle_edit.text():
                command += ["--tle", str(self.tle_edit.text())]
            if self.mle_edit.text():
                command += ["--mle", str(self.mle_edit.text())]

            out = subprocess.check_output(
                command, stderr=subprocess.STDOUT, timeout=4.0
            ).decode()
            self.console.writeLnSignal.emit(out)
        except subprocess.TimeoutExpired as e:
            self.console.writeLnSignal.emit(e.output)
            self.console.writeLnSignal.emit("[-] Test is Timeout")
        except subprocess.CalledProcessError as e:
            self.console.writeLnSignal.emit(e.output)
        self.close()


class TestReactiveDialog(QtWidgets.QDialog):
    def __init__(self, *args, compiled_file: str, settings):
        super().__init__(*args)
        self.console = self.parent().console
        self.compiled_file = compiled_file

        self.judge_command = util.StateFullTextEdit(
            settings, "TEST_COMMAND", self, "./judge"
        )

        self.dialogs = (("Submit...", None), ("JUDGE COMMAND", self.judge_command))
        self.draw()

    def draw(self, *args):
        main_layout = QtWidgets.QVBoxLayout()
        for name, widget in self.dialogs:
            if not widget:
                l_widget = QtWidgets.QGroupBox(name)
                l_widget.setStyleSheet(
                    """
                QGroupBox {
                    color: white;
                    border: 1px solid gray;
                    border-radius: 9px;
                    margin-top: 0.5em;
                }
                QGroupBox::title {
                    color: white;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                """
                )
                l_widget.setFlat(False)
                section_layout = QtWidgets.QFormLayout()
                l_widget.setLayout(section_layout)
                main_layout.addWidget(l_widget)
            else:
                section_layout.addRow(name, widget)
        test_button = QtWidgets.QPushButton("Test")
        test_button.clicked.connect(self.test)
        main_layout.addWidget(test_button)
        self.setLayout(main_layout)

    def test(self):
        for name, widget in self.dialogs:
            try:
                widget.commit()
            except AttributeError:
                pass
        try:
            command = ["oj", "t/r", "-c", self.compiled_file, self.judge_command.text()]

            out = subprocess.check_output(
                command, stderr=subprocess.STDOUT, timeout=4.0
            ).decode()
            self.console.writeLnSignal.emit(out)
        except subprocess.TimeoutExpired as e:
            self.console.writeLnSignal.emit(e.output)
            self.console.writeLnSignal.emit("[-] Test is Timeout")
        except subprocess.CalledProcessError as e:
            self.console.writeLnSignal.emit(e.output)
        self.close()
