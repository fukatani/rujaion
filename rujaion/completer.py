import codecs
from _collections import OrderedDict
import os
import subprocess
from typing import *
from xml.etree import ElementTree

from PyQt5 import QtWidgets, QtCore

from rujaion import util


class CompleterBase(QtWidgets.QCompleter):
    def __init__(self, parent=None):
        super().__init__((), parent)
        self.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.highlighted.connect(self.setHighlighted)
        self.parent = parent
        self.live_templates = load_template(self.live_template_file)
        self.candidates_dict = {}
        self.ng_words = set(
            [
                "alloc_system",
                "alloc_jemalloc",
                "core",
                "compiletest",
                "proc_macro",
                "profiler_builtins",
                "getopts",
                "vec_deque",
                "hash_map",
                "hash_set",
                "hash_state",
                "graphviz",
            ]
        )
        self.lastSelected = ""

    def setHighlighted(self, text: str):
        self.lastSelected = text

    def getSelected(self) -> str:
        return self.lastSelected


class RacerCompleter(CompleterBase):
    # temp file for racer input
    live_template_file = os.path.join(
        util.get_resources_dir(), "live_templates_rust.xml"
    )

    # this is heavy?
    def setCompletionPrefix(self, text: str):
        temp_file_name = util.get_temp_file("rust")
        with codecs.open(temp_file_name, "w", "utf-8") as f:
            f.write(self.parent.toPlainText())
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
                + temp_file_name,
                shell=True,
            ).decode()
        except subprocess.CalledProcessError as e:
            print(e.output)
            return

        self.candidates_dict = {}
        for line in out.split("\n"):
            if line.startswith("MATCH"):
                cand = line[6:].split(",")[0]
                if cand not in self.ng_words:
                    self.candidates_dict[cand] = -1
        search_word = out.split("\n")[0].split(",")[2]

        for live_template in self.live_templates:
            if live_template.name.startswith(search_word):
                self.candidates_dict[live_template.template] = live_template.rpos
        if len(self.candidates_dict) >= 6 or search_word in self.candidates_dict.keys():
            self.candidates_dict = {}
        self.setModel(QtCore.QStringListModel(self.candidates_dict.keys()))
        super().setCompletionPrefix(search_word)


class PyCompleter(CompleterBase):
    live_template_file = os.path.join(
        util.get_resources_dir(), "live_templates_cpp.xml"
    )

    def setCompletionPrefix(self, text: str):
        import jedi

        src_line_num = self.parent.textCursor().blockNumber() + 1
        src_char_num = self.parent.textCursor().columnNumber()
        candidates = jedi.Script(
            self.parent.toPlainText(), src_line_num, src_char_num
        ).completions()
        candidates = [cand.name for cand in candidates]

        self.candidates_dict = {}
        for i, word in enumerate(candidates):
            self.candidates_dict[word] = -1

        self.setModel(QtCore.QStringListModel(self.candidates_dict.keys()))
        super().setCompletionPrefix(text)


class CppCompleter(CompleterBase):
    # temp file for racer input
    live_template_file = os.path.join(
        util.get_resources_dir(), "live_templates_cpp.xml"
    )

    # TODO: Support clang completer
    def setCompletionPrefix(self, text: str):
        temp_file_name = util.get_temp_file("cpp")
        with codecs.open(temp_file_name, "w", "utf-8") as f:
            f.write(self.parent.toPlainText())
        src_line_num = str(self.parent.textCursor().blockNumber() + 1)
        src_char_num = str(self.parent.textCursor().columnNumber())

        try:
            out = subprocess.check_output(
                # read all header is too slow
                # "clang -fsyntax-only -Xclang -code-completion-at=%s:%s:%s %s"
                "clang -cc1 -fsyntax-only -code-completion-at=%s:%s:%s %s"
                % (temp_file_name, src_line_num, src_char_num, temp_file_name),
                shell=True,
            ).decode()
        except subprocess.CalledProcessError as e:
            out = e.output.decode()

        self.candidates_dict = OrderedDict()
        for line in out.split("\n"):
            if line.startswith("COMPLETION:"):
                cand = line.split(" ")[1]
                if text not in cand:
                    continue
                if cand not in self.ng_words:
                    self.candidates_dict[cand] = -1

        for live_template in self.live_templates:
            if live_template.name.startswith(text):
                self.candidates_dict[live_template.template] = live_template.rpos
        if len(self.candidates_dict) >= 10 or text in self.candidates_dict.keys():
            self.candidates_dict = {}
        self.setModel(QtCore.QStringListModel(self.candidates_dict.keys()))
        super().setCompletionPrefix(text)


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
