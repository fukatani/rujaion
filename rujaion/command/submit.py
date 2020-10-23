from PyQt5 import QtWidgets

from rujaion import util


class SubmitDialog(QtWidgets.QDialog):
    def __init__(self, *args, url: str, lang: str, settings=None):
        super().__init__(*args)
        self.url_edit = util.StateLessTextEdit(url, self)
        self.lang_edit = util.StateLessTextEdit(lang, self)
        self.dialogs = [
            ("Submit...", None),
            ("URL", self.url_edit),
            ("Language", self.lang_edit),
        ]

        self.submitter = util.Commander(self.parent().console)
        self.resize(500, 100)
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
        submit_button = QtWidgets.QPushButton("Submit")
        submit_button.clicked.connect(self.submit)
        main_layout.addWidget(submit_button)
        self.setLayout(main_layout)
        # self.adjustSize()

    def submit(self):
        for name, widget in self.dialogs:
            try:
                widget.commit()
            except AttributeError:
                pass
        cmd = [
            "oj",
            "s",
            "-w",
            "0.3",
            "-l",
            self.lang_edit.text(),
            "-y",
            self.url_edit.text(),
            self.parent().editor.fname,
            # "--no-open",
        ]
        print(cmd)
        self.submitter.cmd = cmd
        self.submitter.start()
        self.close()
