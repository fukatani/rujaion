import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class WebViewWindow(QWidget):

    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.url = ""
        self.browser = QWebEngineView()
        self.browser.load(QUrl(self.url))
        self.browser.resize(1000,600)
        self.browser.move(200,200)
        self.browser.setWindowTitle("Task")

        grid = QGridLayout()
        grid.addWidget(self.browser,2, 0, 5, 15)
        self.setLayout(grid)
        self.resize(500, 800)

    def loadPage(self):
        if self.url:
           self.browser.load(QUrl(self.url))

    def changePage(self, url):
        self.url = url
        self.loadPage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WebViewWindow()
    sys.exit(app.exec_())
