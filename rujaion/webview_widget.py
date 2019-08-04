from http.cookiejar import Cookie
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript

from onlinejudge.dispatch import service_from_url
from onlinejudge._implementation.utils import (
    default_cookie_path,
    with_cookiejar,
    new_session_with_our_user_agent,
)
from PyQt5.QtNetwork import QNetworkCookie

# Many of source is copied from https://qiita.com/montblanc18/items/88d0b639de86b7cac613


navi_script = """(function() {
    'use strict';
    if (!location.href.match(/^https:\/\/atcoder\.jp\/contests\/([^\/]+)/)) {
        return;
    }
    const contest_name = location.href.match(/^https:\/\/atcoder\.jp\/contests\/([^\/]+)/)[1];
    const key = 'atcoder-optimizer-' + contest_name;
     if (location.href.match(/^https:\/\/atcoder\.jp\/contests\/([^\/]+)\/tasks\/?$/)) {
        const problems = [];
        const rows = document.querySelectorAll('tbody>tr');
        for (let i = 0; i < rows.length; i++) {
            const links = rows[i].querySelectorAll('a');
            const href = links[0].getAttribute('href');
            const text = links[0].textContent + ' - ' + links[1].textContent;
            problems.push({
                href: href,
                text: text
            });
        }
        localStorage[key] = JSON.stringify(problems);
    }
     if (key in localStorage) {
        var dom_obj = document.getElementById("main-container");
        dom_obj.style.paddingTop = "0px";

        if (document.getElementById("sourceCode")) {
           var dom_obj = document.getElementById("sourceCode");
           var dom_obj_parent = dom_obj.parentNode.parentNode.parentNode;
           dom_obj_parent.removeChild(dom_obj.parentNode.parentNode);

           var dom_obj = document.getElementsByTagName("footer")[0];
           var dom_obj_parent = dom_obj.parentNode.parentNode;
           dom_obj_parent.removeChild(dom_obj.parentNode);
        }

        let problems = JSON.parse(localStorage[key]);
        const problemsBar = document.createElement('ul');
        problemsBar.className = 'nav nav-tabs';
        for (let i = 0; i < problems.length; i++) {
            const link = document.createElement('a');
            link.setAttribute('style', 'margin-left: 10px; margin-right: 10px; white-space: nowrap');
            link.setAttribute('href', problems[i].href);
            link.textContent = problems[i].text;
            const span = document.createElement('span');
            span.textContent = ' ';
            span.appendChild(link);
            problemsBar.appendChild(span);
        }
        document.getElementById('contest-nav-tabs').innerHTML = '';
        document.getElementById('contest-nav-tabs').appendChild(problemsBar);
    }
})();"""


class CustomWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runScript()
        self.setZoomFactor(0.97)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        menu = QtWidgets.QMenu()
        menu.addAction(u"Go Next Task", self.parent().goNextTask)
        menu.addAction(u"Go Previous Task", self.parent().goPreviousTask)
        menu.exec(a0.globalPos())

    def runScript(self) -> None:
        # self.page().runJavaScript(navi_scripts, QWebEngineScript.ApplicationWorld)
        script = QWebEngineScript()
        script.setName("ac-navigator")
        script.setSourceCode(navi_script)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        self.page().scripts().insert(script)


class WebViewWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.browser = CustomWebEngineView(self)
        self.browser.resize(1000, 600)
        self.browser.setWindowTitle("Task")
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.returnPressed.connect(self.loadPage)
        self.browser.urlChanged.connect(self.updateCurrentUrl)
        session = new_session_with_our_user_agent()
        self.browser.page().profile().setHttpUserAgent(session.headers["User-Agent"])
        self.browser.page().profile().cookieStore().cookieAdded.connect(
            self.handleCookieAdded
        )
        self.browser.loadFinished.connect(self.download_task)

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

    def focusOnUrlEdit(self):
        self.url_edit.setFocus()
        self.url_edit.selectAll()

    def handleCookieAdded(self, cookie: QNetworkCookie):
        url = self.browser.url().toString()
        if service_from_url(url):
            py_cookie = toPyCookie(cookie)
            with with_cookiejar(
                new_session_with_our_user_agent(), path=default_cookie_path
            ) as sess:
                sess.cookies.set_cookie(py_cookie)


def toPyCookie(qt_cookie: QNetworkCookie) -> Cookie:
    port = None
    port_specified = False
    secure = qt_cookie.isSecure()
    name = qt_cookie.name().data().decode()
    value = qt_cookie.value().data().decode()
    v = qt_cookie.path()
    path_specified = bool(v != "")
    path = v if path_specified else None
    v = qt_cookie.domain()
    domain_specified = bool(v != "")
    domain = v
    if domain_specified:
        domain_initial_dot = v.startswith(".")
    else:
        domain_initial_dot = None
    v = int(qt_cookie.expirationDate().toTime_t())
    expires = 2147483647 if v > 2147483647 else v
    rest = {"HttpOnly": qt_cookie.isHttpOnly()}
    discard = False
    return Cookie(
        0,
        name,
        value,
        port,
        port_specified,
        domain,
        domain_specified,
        domain_initial_dot,
        path,
        path_specified,
        secure,
        expires,
        discard,
        None,
        None,
        rest,
    )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = WebViewWindow()
    ex.show()
    sys.exit(app.exec_())
