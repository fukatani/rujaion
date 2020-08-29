from http.cookiejar import Cookie
import subprocess
import sys

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import QThread, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtNetwork import QNetworkCookie

from onlinejudge_workaround_for_conflict import dispatch
from onlinejudge_workaround_for_conflict._implementation.utils import (
    default_cookie_path,
)
from onlinejudge_command.utils import new_session_with_our_user_agent

from rujaion import util

# Many of source is copied from https://qiita.com/montblanc18/items/88d0b639de86b7cac613


navi_script = """// ==UserScript==
// @match        https://atcoder.jp/contests/*
// ==/UserScript==
(function() {
    'use strict';
    if (!location.href.match(/^https:\/\/atcoder\.jp\/contests\/([^\/]+)/)) {
        return;
    }
    const contest_name = location.href.match(/^https:\/\/atcoder\.jp\/contests\/([^\/]+)/)[1];
    const key = 'atcoder-optimizer-' + contest_name;
     if (location.href.match(/^https:\/\/atcoder\.jp\/contests\/([^\/]+)\/tasks\/?$/)) {
        const tasks = [];
        let row;
        for (row of document.querySelectorAll('tbody > tr')) {
            const task = row.querySelectorAll('a');
            const href = task[0].getAttribute('href');
            const task_number = task[0].textContent;
            const task_name = task[1].textContent;
            tasks.push({
                href: href,
                task_name: task_number + ' - ' + task_name
            });
        }
        localStorage[key] = JSON.stringify(tasks);
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
        if (document.getElementsByClassName("alert alert-warning alert-dismissible fade in")) {
           var obj = document.getElementsByClassName("alert alert-warning alert-dismissible fade in")[0]
           obj.innerHTML = '';
        }

        const tasksBar = document.createElement('l');
        tasksBar.className = 'nav nav-tabs';
        let task;
        for (task of JSON.parse(localStorage[key])) {
            const link = document.createElement('a');
            link.setAttribute('style', 'margin-right: 20px;');
            link.setAttribute('href', task.href);
            link.textContent = task.task_name;
            tasksBar.appendChild(link);
        }
        document.getElementById('contest-nav-tabs').innerHTML = '';
        document.getElementById('contest-nav-tabs').appendChild(tasksBar);
    }
})();"""


yukicoder_script = """// ==UserScript==
// @match        https://yukicoder.me/problems/*
// ==/UserScript==
(function() {
    'use strict';
    var dom_obj = document.getElementById("sidebar");
    var dom_obj_parent = dom_obj.parentNode;
    dom_obj_parent.removeChild(dom_obj);
})();"""


class CustomWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runScript()
        self.setZoomFactor(0.97)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        menu = QtWidgets.QMenu()
        if self.parent().next_prev_updater.next is not None:
            menu.addAction(u"Go Next Task", self.parent().goNextTask)
        if self.parent().next_prev_updater.prev is not None:
            menu.addAction(u"Go Previous Task", self.parent().goPreviousTask)
        if self.selectedText():
            menu.addAction(u"View Graph", self.viewGraph)
        menu.addAction(u"Back", self.back)
        menu.addSeparator()
        if self.parent().next_prev_updater.problems is not None:
            problems = self.parent().next_prev_updater.problems
            for i, problem_url in enumerate(problems):
                problem_id = problem_url.split("/")[-1]
                # I know this is not good code.
                # But commented out code does not works
                # menu.addAction(
                #     u"Go to {}".format(problem_id),
                #     lambda: self.parent().changePage(problem)
                # )
                if i == 0:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[0]),
                    )
                elif i == 1:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[1]),
                    )
                elif i == 2:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[2]),
                    )
                elif i == 3:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[3]),
                    )
                elif i == 4:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[4]),
                    )
                elif i == 5:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[5]),
                    )
                elif i == 6:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[6]),
                    )
                elif i == 7:
                    menu.addAction(
                        u"Go to {}".format(problem_id),
                        lambda: self.parent().changePage(problems[7]),
                    )
        menu.exec(a0.globalPos())

    def runScript(self) -> None:
        # self.page().runJavaScript(navi_scripts, QWebEngineScript.ApplicationWorld)
        script = QWebEngineScript()
        script.setName("atcoder-optimizer")
        script.setSourceCode(navi_script)
        script.setInjectionPoint(QWebEngineScript.DocumentReady)
        script.setRunsOnSubFrames(True)
        script.setWorldId(QWebEngineScript.ApplicationWorld)
        self.page().scripts().insert(script)

    def viewGraph(self) -> None:
        text = self.selectedText()
        graph_member = []
        weighted = "false"

        lines = text.split("\n")
        vertexes = []
        for line in lines:
            words = line.split(" ")
            if len(words) < 2:
                continue
            if len(words) == 3:
                weighted = "true"
            graph_member.append("-".join(words))
            vertexes.append(int(words[0]))
            vertexes.append(int(words[1]))

        if min(vertexes) == 0:
            indexed = "false"
        else:
            indexed = "true"

        max_vertex = max(vertexes)
        if indexed == "false":
            max_vertex -= 1
        graph_member = ["{0}-{1}".format(max_vertex, len(lines))] + graph_member
        graph_query = ",".join(graph_member)

        url = "https://hello-world-494ec.firebaseapp.com/?format=true&directed=false&weighted={0}&indexed={1}&data={2}".format(
            weighted, indexed, graph_query
        )
        try:
            subprocess.Popen(["sensible-browser", url])
        except subprocess.TimeoutExpired:
            pass


class WebViewWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        super().__init__(parent, *args)
        self.browser = CustomWebEngineView(self)
        self.browser.resize(1000, 600)
        self.browser.setWindowTitle("Task")
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.returnPressed.connect(self.loadPage)
        with new_session_with_our_user_agent(path=default_cookie_path) as session:
            self.browser.page().profile().setHttpUserAgent(
                session.headers["User-Agent"]
            )
        self.browser.page().profile().cookieStore().cookieAdded.connect(
            self.handleCookieAdded
        )
        self.browser.loadFinished.connect(self.download_task)

        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.url_edit, 0, 0, 1, 15)
        grid.addWidget(self.browser, 1, 0, 5, 15)
        self.setLayout(grid)
        self.resize(800, 800)
        self.next_prev_updater = NextPreviousProblemUpdater()

    def download_task(self):
        self.url_edit.setText(self.browser.url().toString())
        self.next_prev_updater.url = self.browser.url().toString()
        self.next_prev_updater.start()
        self.url_edit.setText(self.browser.url().toString())
        self.parent().parent().download(self.url_edit.text())

    def loadPage(self):
        self.next_prev_updater.reset()
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
        """
        if self.next_prev_updater.next is not None:
            self.changePage(self.next_prev_updater.next)

    def goPreviousTask(self):
        """ Go previous contest task.
        ex.
        https://atcoder.jp/contests/cpsco2019-s2/tasks/cpsco2019_s2_b ->
        https://atcoder.jp/contests/cpsco2019-s2/tasks/cpsco2019_s2_a
        """
        if self.next_prev_updater.prev is not None:
            self.changePage(self.next_prev_updater.prev)

    def focusOnUrlEdit(self):
        self.url_edit.setFocus()
        self.url_edit.selectAll()

    def handleCookieAdded(self, cookie: QNetworkCookie):
        url = self.browser.url().toString()
        if dispatch.service_from_url(url):
            py_cookie = toPyCookie(cookie)
            util.OJ_MUTEX.lock()
            with new_session_with_our_user_agent(path=default_cookie_path) as sess:
                sess.cookies.set_cookie(py_cookie)
            util.OJ_MUTEX.unlock()


class NextPreviousProblemUpdater(QThread):
    def __init__(self):
        super().__init__()
        self.url = ""
        self.next = None
        self.prev = None
        self.problems = None

    def reset(self):
        self.next = None
        self.prev = None
        # self.problems = None

    def run(self):
        cur_problem = dispatch.problem_from_url(self.url)
        if cur_problem is None:
            return
        if cur_problem.get_service().get_name() == "yukicoder":
            words = self.url.split("?")
            words = words[0].split("/")
            prev_words = words.copy()
            try:
                problem_no = int(words[-1])
            except ValueError:
                return
            prev_words[-1] = str(problem_no - 1)
            next_words = words.copy()
            next_words[-1] = str(problem_no + 1)
            self.prev = "/".join(prev_words)
            self.next = "/".join(next_words)
            return
        try:
            contest = cur_problem.get_contest()
            with new_session_with_our_user_agent(path=default_cookie_path) as sess:
                problems = contest.list_problems(session=sess)
            for i, problem in enumerate(problems):
                if problem == cur_problem:
                    self.prev = problems[i - 1].get_url()
                    self.next = problems[(i + 1) % len(problems)].get_url()
                    break
            self.problems = [problem_url.get_url() for problem_url in problems]
        except Exception:
            pass


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
