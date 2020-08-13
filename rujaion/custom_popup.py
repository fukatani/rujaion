import subprocess
import sys
import time

from onlinejudge_workaround_for_conflict._implementation.utils import (
    default_cookie_path,
)
from onlinejudge_command.utils import new_session_with_our_user_agent

from onlinejudge_workaround_for_conflict.dispatch import submission_from_url
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class External(QThread):
    updateRequest = pyqtSignal(object)
    finishRequest = pyqtSignal()
    failed_words = ("WA", "RE", "TLE", "MLE", "RE", "CE")

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            with new_session_with_our_user_agent(path=default_cookie_path) as sess:
                finished = False
                for i in range(40):
                    time.sleep(2)
                    submission = submission_from_url(self.url)
                    result = submission.download_data(session=sess)
                    self.updateRequest.emit((result.status, result.problem_id))
                    result = result.status
                    failed = any([word in result for word in self.failed_words])
                    if result == "AC" or failed:
                        finished = True
                    if failed:
                        subprocess.check_call(
                            ["sensible-browser", submission.get_url()],
                            stdin=sys.stdin,
                            stdout=sys.stdout,
                            stderr=sys.stderr,
                        )
                        finished = True
                    if finished:
                        break
        except Exception as e:
            print(e)
        time.sleep(3)
        self.finishRequest.emit()


class CustomPopup(QtWidgets.QWidget):
    def __init__(self, parent, url: str, **kwargs):
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
        self.move(QtGui.QCursor.pos())
        self.run(url)

    def run(self, url: str):
        self.ext = External(url)
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

    w = CustomPopup(url="https://atcoder.jp/contests/diverta2019/submissions/5363629")
    w.show()
    sys.exit(app.exec_())
