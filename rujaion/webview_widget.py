import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Many of source is copied from https://qiita.com/montblanc18/items/88d0b639de86b7cac613


class CustomWebEngineView(QWebEngineView):
    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(u"Go Next Task", self.parent().goNextTask)
        menu.addAction(u"Go Previous Task", self.parent().goPreviousTask)
        menu.exec(a0.globalPos())


class WebViewWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.browser = CustomWebEngineView(self)
        self.browser.resize(1000, 600)
        self.browser.setWindowTitle("Task")
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.returnPressed.connect(self.loadPage)
        self.browser.urlChanged.connect(self.updateCurrentUrl)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.url_edit, 0, 0, 1, 15)
        grid.addWidget(self.browser, 1, 0, 5, 15)
        self.setLayout(grid)
        self.resize(800, 800)

    def download_task(self):
        self.url_edit.setText(self.browser.url().toString())
        self.parent().parent().download(self.url_edit.text())

    def loadPage(self):
        if self.url_edit.text():
            self.browser.load(QUrl(self.url_edit.text()))

    def changePage(self, url: str):
        self.url_edit.setText(url)
        self.loadPage()

    def goNextTask(self):
        """ Go next contest task.
        ex.
        https://atcoder.jp/contests/cpsco2019-s2/tasks/cpsco2019_s2_e ->
        https://atcoder.jp/contests/cpsco2019-s2/tasks/cpsco2019_s2_f

        This function is note tested except AtCoder.
        """
        current_url = self.browser.url().toString()
        if current_url[-1] == "z":
            return
        current_url = current_url[:-1] + chr(ord(current_url[-1]) + 1)
        self.changePage(current_url)

    def goPreviousTask(self):
        """ Go previous contest task.
        ex.
        https://atcoder.jp/contests/cpsco2019-s2/tasks/cpsco2019_s2_b ->
        https://atcoder.jp/contests/cpsco2019-s2/tasks/cpsco2019_s2_a

        This function is note tested except AtCoder.
        """
        current_url = self.browser.url().toString()
        if current_url[-1] == "a":
            return
        current_url = current_url[:-1] + chr(ord(current_url[-1]) - 1)
        self.changePage(current_url)

    def updateCurrentUrl(self):
        """ Rewriting url_edit when you move different web page.
        """
        self.url_edit.clear()
        self.url_edit.insert(self.browser.url().toString())
        # auto task download
        if self.parent() is not None:
            self.parent().parent().download(self.url_edit.text(), browser_reflesh=False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = WebViewWindow()
    ex.show()
    sys.exit(app.exec_())
