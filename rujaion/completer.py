import codecs
import os
import subprocess
from typing import *
from xml.etree import ElementTree

from PyQt5 import QtWidgets, QtCore


class RacerCompleter(QtWidgets.QCompleter):
    # temp file for racer input
    temp_file_name = os.path.join(os.path.dirname(__file__), "temp.rs")
    live_template_file = os.path.join(os.path.dirname(__file__), "live_templates.xml")

    def __init__(self, parent=None):
        super().__init__((), parent)
        self.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.highlighted.connect(self.setHighlighted)
        self.parent = parent
        self.live_templates = load_template(self.live_template_file)
        self.candidates_dict = {}
        self.ng_words = "core"
        self.lastSelected = ""

    def setHighlighted(self, text: str):
        self.lastSelected = text

    def getSelected(self) -> str:
        return self.lastSelected

    # this is heavy?
    def setCompletionPrefix(self, text: str):
        temp_file = codecs.open(self.temp_file_name, "w", "utf-8")
        temp_file.write(self.parent.toPlainText())
        temp_file.close()
        src_line_num = str(self.parent.textCursor().blockNumber() + 1)
        src_char_num = str(self.parent.textCursor().columnNumber())

        try:
            out = subprocess.check_output(
                "racer complete"
                + " "
                + src_line_num
                + " "
                + src_char_num
                + " "
                + self.temp_file_name,
                shell=True,
            ).decode()
        except Exception:
            return

        self.candidates_dict = {}
        for line in out.split("\n"):
            if line.startswith("MATCH"):
                cand = line[6:].split(",")[0]
                if cand not in self.ng_words:
                    self.candidates_dict[line[6:].split(",")[0]] = -1
        search_word = out.split("\n")[0].split(",")[2]

        for live_template in self.live_templates:
            if search_word in live_template.name:
                self.candidates_dict[live_template.template] = live_template.rpos
        if len(self.candidates_dict) >= 6 or search_word in self.candidates_dict.keys():
            self.candidates_dict = {}
        self.setModel(QtCore.QStringListModel(self.candidates_dict.keys()))
        super().setCompletionPrefix(search_word)


class LiveTemplate:
    def __init__(self):
        self.name = ""
        self.body = ""
        self.variables = []
        self.default_values = []
        self.template = ""
        self.rpos = -1

    def generate(self):
        self.template = self.body
        for var, value in zip(self.variables, self.default_values):
            if value is not None:
                self.template = self.template.replace("$" + var + "$", value)
        if "$END$" in self.template:
            self.rpos = len(self.template) - self.template.find("$END$") - 5
        self.template = self.template.replace("$END$", "")


def load_template(xml_file_name: str) -> List[LiveTemplate]:
    if not os.path.isfile(xml_file_name):
        return []
    with open(xml_file_name) as f:
        xml = f.read()
    root = ElementTree.fromstring(xml)
    templates = []
    for template in root.findall("template"):
        new_template = LiveTemplate()
        new_template.name = template.get("name")
        new_template.body = template.get("value")
        for variable in template.findall("variable"):
            new_template.variables.append(variable.get("name"))
            if "defaultValue" in variable.keys():
                new_template.default_values.append(variable.get("defaultValue"))
            else:
                new_template.default_values.append(None)
        new_template.generate()
        templates.append(new_template)
    return templates
