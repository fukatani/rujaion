import sys

import pandas

from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtCore import Qt


table_style = (
    "table{width: 50%; border-collapse: collapse; border-spacing: 0;}"
    "table th,table td{ padding: 3px 0; text-align: center;} "
    "table tr:nth-child(odd){background-color: #ddd} "
    "body{font-family: arial}"
)


class TableView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.insertStyleSheet()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMaximumSize(700, 600)
        self.setWindowTitle("Table View")

    def insertStyleSheet(self):
        name = "table_style"
        s = """(function() {
    css = document.createElement('style');
    css.type = 'text/css';
    css.id = '%s';
    document.head.appendChild(css);
    css.innerText = '%s';
})()""" % (
            name,
            table_style,
        )
        self.page().runJavaScript(s, QWebEngineScript.ApplicationWorld)
        script = QWebEngineScript()
        script.setName(name)
        script.setSourceCode(s)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        self.page().scripts().insert(script)

    def visualize_tables(self, text: str):
        htmls = []
        for line in text.split(u"\u2029"):
            if "[" in line:
                start_idx = line.find("[")
                end_idx = line.rfind("]")
                try:
                    table = pandas.read_json(line[start_idx : end_idx + 1])
                except ValueError:
                    continue
                htmls.append(table.to_html())
                print(table.to_html())
        html = "<br>".join(htmls)
        self.setHtml(html)


if __name__ == "__main__":
    text = (
        "v = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]\n"
        + "v = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]"
    )
    app = QtWidgets.QApplication(sys.argv)
    ex = TableView()
    ex.visualize_tables(text)
    ex.show()
    sys.exit(app.exec_())
