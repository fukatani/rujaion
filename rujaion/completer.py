import codecs
import os
import subprocess

from PyQt5 import QtWidgets, QtCore


class RacerCompleter(QtWidgets.QCompleter):
    insertText = QtCore.pyqtSignal(str)
    temp_text = os.path.join(os.path.dirname(__file__), "temp.rs")

    def __init__(self, parent=None):
        super().__init__((), parent)
        self.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.highlighted.connect(self.setHighlighted)
        self.parent = parent

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected

    # this is heavy?
    def setCompletionPrefix(self, text):
        fname = codecs.open(self.temp_text, "w", "utf-8")
        fname.write(self.parent.toPlainText())
        fname.close()
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
                + self.temp_text,
                shell=True,
            ).decode()
        except Exception:
            return
        candidates = []
        for line in out.split("\n"):
            if line.startswith("MATCH"):
                candidates.append(line[6:].split(",")[0])
        if len(candidates) >= 6 or text in candidates:
            candidates = []
        self.setModel(QtCore.QStringListModel(candidates))
        super().setCompletionPrefix(text)
