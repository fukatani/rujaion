import subprocess

from PyQt5 import QtWidgets


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, *args, settings=None):
        super().__init__(*args)
        self.settings = settings
        self.dialogs = (
            ("Login Settings", None),
            ("URL", URLEdit(self.settings, self)),
            ("Account Name", AccountEdit(self.settings, self)),
            ("Password", PasswordEdit(self.settings, self)),
        )
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
        login_button.clicked.connect(self.close)
        main_layout.addWidget(login_button)
        self.setLayout(main_layout)

    def close(self):
        for name, widget in self.dialogs:
            try:
                widget.commit()
            except AttributeError:
                pass
        self.settings.sync()
        cmd = (
            "oj",
            "l",
            "-u",
            self.settings.value("Account", type=str),
            "-p",
            self.settings.value("Password", type=str),
            self.settings.value("Login URL", type=str),
        )
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        self.parent().console.write(out)
        super().close()


class URLEdit(QtWidgets.QLineEdit):
    def __init__(self, settings, parent):
        self.parent = parent
        self.settings = settings
        super().__init__()
        v = settings.value("Login URL", type=str)
        self.setText(v)

    def commit(self):
        self.settings.setValue("Login URL", self.text())


class AccountEdit(QtWidgets.QLineEdit):
    def __init__(self, settings, parent):
        self.parent = parent
        self.settings = settings
        super().__init__()
        v = settings.value("Account", type=str)
        self.setText(v)

    def commit(self):
        self.settings.setValue("Account", self.text())


class PasswordEdit(QtWidgets.QLineEdit):
    def __init__(self, settings, parent):
        self.parent = parent
        self.settings = settings
        super().__init__()
        self.setEchoMode(QtWidgets.QLineEdit.Password)

    def commit(self):
        pass
