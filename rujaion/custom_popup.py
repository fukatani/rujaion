import subprocess
import sys
import time

from onlinejudge._implementation.utils import (
    default_cookie_path,
    with_cookiejar,
    new_session_with_our_user_agent,
)
from onlinejudge.service import atcoder
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class External(QThread):
    updateRequest = pyqtSignal(object)
    finishRequest = pyqtSignal()

    def __init__(self, submission, url):
        super().__init__()
        self.submission = submission
        self.url = url

    def run(self):
        finished = False
        with with_cookiejar(
            new_session_with_our_user_agent(), path=default_cookie_path
        ) as sess:
            for i in range(20):
                time.sleep(2)
                self.submission = atcoder.AtCoderSubmission.from_url(self.url)
                result = self.submission.get_status(session=sess)
                self.updateRequest.emit((result, self.submission._problem_id))
                if result == "AC" or "WA" in result or "RE" in result:
                    finished = True
                if "WA" in result or "RE" in result:
                    subprocess.check_call(
                        ["sensible-browser", self.submission.get_url()],
                        stdin=sys.stdin,
                        stdout=sys.stdout,
                        stderr=sys.stderr,
                    )
                    finished = True
                if finished:
                    time.sleep(3)
                    self.finishRequest.emit()
                    break


class CustomPopup(QtWidgets.QWidget):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.setWindowOpacity(0.7)
        # self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("CustomPopup")

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
        self.label = QtWidgets.QLabel(" " * 50, self)
        self.url = kwargs["url"]
        self.move(QtGui.QCursor.pos())
        self.submission = atcoder.AtCoderSubmission.from_url(self.url)
        self.run()

    def run(self):
        self.ext = External(self.submission, self.url)
        self.ext.updateRequest.connect(self.update)
        self.ext.finishRequest.connect(self.finish)
        self.ext.start()

    def update(self, result):
        result, problem_id = result
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.move(25, 35)

        print("submit result: " + problem_id + " " + result)
        self.label.setText(
            "<font color='white'>" + problem_id + ": " + result + "</font>"
        )

        if result == "AC":
            self.setStyleSheet("background-color: green")
        elif result == "WJ" or (
            "/" in result and "WA" not in result and "RE" not in result
        ):
            self.setStyleSheet("background-color: grey")
        else:
            self.setStyleSheet("background-color: orange")
        self.repaint()

    def finish(self):
        self.ext.exit(0)
        self.close()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    w = CustomPopup(
        None, url="https://atcoder.jp/contests/diverta2019/submissions/5363629"
    )
    w.show()
    sys.exit(app.exec_())
