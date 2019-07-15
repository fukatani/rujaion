import subprocess
import sys
import time

from onlinejudge._implementation.utils import default_cookie_path, with_cookiejar, new_session_with_our_user_agent
from onlinejudge.service import atcoder
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class External(QThread):
    updateRequest = pyqtSignal()
    def run(self):
        self.updateRequest.emit()
        for i in range(20):
            time.sleep(3)
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

        with with_cookiejar(new_session_with_our_user_agent(),
                                  path=default_cookie_path) as sess:
            self.submission = atcoder.AtCoderSubmission.from_url(self.url)
            result = self.submission.get_status(session=sess)
            print("submit result: " + result)
            self.label.setText(
                "<font color='white'>" +
                self.submission._problem_id + ": " + result +
                "</font>"
            )

            if result == "AC":
                self.setStyleSheet("background-color: green")
                self.finished = True
            elif result == "WJ" or \
                ("/" in result and "WA" not in result):
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
