from PyQt5 import QtWidgets, QtGui

from rujaion import util


class ExtractDialog(QtWidgets.QDialog):
    def __init__(self, *args, sentence: str):
        super().__init__(*args)
        self.sentence_edit = util.StateLessTextEdit(sentence, self)
        self.name_edit = util.StateLessTextEdit("", self)

        self.extract_kind_box = QtWidgets.QGroupBox("Extract kind")
        vbox = QtWidgets.QVBoxLayout()
        self.extract_var = QtWidgets.QRadioButton("As Variable")
        self.extract_var.setChecked(True)
        vbox.addWidget(self.extract_var)
        self.extract_type = QtWidgets.QRadioButton("As Type")
        vbox.addWidget(self.extract_type)
        self.extract_kind_box.setLayout(vbox)
        self.replace_all_checkbox = QtWidgets.QCheckBox()
        self.replace_all_checkbox.setChecked(True)

        self.dialogs = (
            ("Extract...", None),
            ("Sentence", self.sentence_edit),
            ("Name", self.name_edit),
            ("Kind", self.extract_kind_box),
            ("Replace All", self.replace_all_checkbox),
        )
        self.resize(500, 100)
        self.draw()
        self.name_edit.setFocus()

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
        extract_button = QtWidgets.QPushButton("Extract")
        extract_button.clicked.connect(self.extract)
        main_layout.addWidget(extract_button)
        self.setLayout(main_layout)

    def extract(self):
        if self.extract_var.isChecked():
            declaration = "let {} = {};\n".format(
                self.name_edit.text(), self.sentence_edit.text()
            )

        if self.extract_type.isChecked():
            declaration = "type {} = {};\n".format(
                self.name_edit.text(), self.sentence_edit.text()
            )

        if self.replace_all_checkbox.isChecked():
            pos = self.parent().save_position()
            text = self.parent().toPlainText()
            self.parent().clear_and_write_text(
                text.replace(self.sentence_edit.text(), self.name_edit.text())
            )
            self.parent().load_position(*pos)

        tc = self.parent().textCursor()
        tc.movePosition(QtGui.QTextCursor.StartOfLine)
        tc.insertText(declaration)
        self.close()
