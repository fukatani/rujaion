import subprocess

from PyQt5 import QtWidgets

from rujaion import util


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, *args, url: str, settings=None):
        super().__init__(*args)
        self.settings = settings
        self.password_edit = util.StateLessTextEdit("", self)
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.url_edit = util.StateLessTextEdit(url, self)
        self.dialogs = (
            ("Login Settings", None),
            ("URL", self.url_edit),
            ("Account Name", util.StateFullTextEdit(self.settings, "Account", self)),
            ("Password", self.password_edit),
        )
        self.resize(500, 100)
        self.draw()

    def draw(self, *args, settings=None):
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
        login_button = QtWidgets.QPushButton("Login")
        login_button.clicked.connect(self.login)
        main_layout.addWidget(login_button)
        self.setLayout(main_layout)

    def login(self):
        for name, widget in self.dialogs:
            try:
                widget.commit()
            except AttributeError:
                pass
        self.settings.sync()
        cmd = (
            "oj",
            "l",
            "--use-browser",
            "never",
            "-u",
            self.settings.value("Account", type=str),
            "-p",
            self.password_edit.text(),
            self.url_edit.text(),
        )
        try:
            util.OJ_MUTEX.lock()
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            util.OJ_MUTEX.unlock()
            self.parent().console.writeLnSignal.emit(out)
        except subprocess.CalledProcessError as err:
            self.parent().console.writeLnSignal.emit(err.output)
        self.close()


class URLEdit(QtWidgets.QLineEdit):
    def __init__(self, url: str, parent):
        super().__init__()
        self.parent = parent
        self.setText(url)

    def commit(self):
        pass
