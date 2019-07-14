import subprocess
import sys
import time

from onlinejudge.service import atcoder
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class External(QThread):
    updateRequest = pyqtSignal()
    def run(self):
        self.updateRequest.emit()
        for i in range(20):
            time.sleep(2)
            self.updateRequest.emit()


class CustomPopup(QtWidgets.QWidget):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.setWindowOpacity(0.7)
        # self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('CustomPopup')

        # set style
        radius = 40.0
        path = QtGui.QPainterPath()
        self.resize(220, 90)
        path.addRoundedRect(QtCore.QRectF(self.rect()), radius, radius)
        mask = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        # set background
        self.setAutoFillBackground(True)

        # set label
        self.label = QtWidgets.QLabel("", self)
        self.url = kwargs["url"]
        self.move(QtGui.QCursor.pos())
        # self.submission = atcoder.AtCoderSubmission.from_url(self.url)
        self.submission = None
        self.finished = False
        self.update()
        self.run()

    def run(self):
        self.ext = External()
        self.ext.updateRequest.connect(self.update)
        self.ext.start()

    def update(self):
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.move(25, 35)

        self.submission = atcoder.AtCoderSubmission.from_url(self.url)
        print("submit result: " + self.submission.get_status())
        self.label.setText(
            "<font color='white'>" +
            self.submission._problem_id + ": " + self.submission.get_status() +
            "</font>"
        )


        if self.submission.get_status() == "AC":
            self.setStyleSheet("background-color: green")
            self.finished = True
        elif self.submission.get_status() == "WJ" or "/" in self.submission.get_status():
            self.setStyleSheet("background-color: grey")
        else:
            self.setStyleSheet("background-color: orange")
            if not self.finished:
                subprocess.check_call(["sensible-browser", self.submission.get_url()],
                                      stdin=sys.stdin, stdout=sys.stdout,
                                      stderr=sys.stderr)
            self.finished = True
        self.repaint()
        if self.finished:
            # self.ext.exit(0)
            time.sleep(3)
            self.close()

    def mousePressEvent(self, event):
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    w = CustomPopup(None,
                    url="https://atcoder.jp/contests/diverta2019/submissions/5363629")
    w.show()
    sys.exit(app.exec_())

