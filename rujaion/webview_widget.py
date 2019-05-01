import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class PersephoneWindow(QWidget):

    def __init__(self):
        super().__init__()
        # self.initUI()
        self.url = 'https://www.google.co.jp'

        # setting browser
        self.browser = QWebEngineView()
        self.browser.load(QUrl(self.url))
        self.browser.resize(1000,600)
        self.browser.move(200,200)
        self.browser.setWindowTitle("Task")

        # setting layout
        grid = QGridLayout()
        grid.addWidget(self.browser,2, 0, 5, 15)
        self.setLayout(grid)
        self.resize(1200, 800)
        # self.center()
        self.show()

    def loadPage(self):
        self.browser.load(QUrl(self.url))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PersephoneWindow()
    sys.exit(app.exec_())
