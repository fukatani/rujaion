Rujaion : Rust / C++ / Python IDE specialized in online judge 
==============================
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

[![Travis](https://img.shields.io/travis/fukatani/rujaion.svg)](https://travis-ci.org/fukatani/rujaion)
[![PyPI](https://img.shields.io/pypi/v/Rujaion.svg)](https://pypi.python.org/pypi/Rujaion)
![screen_cast](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/rujaion.gif)

Introduction
==============================
Lightweight Rust IDE based on PyQt. (C++ and Python support is experimental)

This IDE is simplified and specialized to competitive programming, user can concentrate on programming and can achieve best performance.

When you open the contest problem page, input and output example of the problem is downloaded automatically in the background.

Then testing with sample cases, debugging with test cases, and submission can be by one click.

Feature
==============================
* Rust / C++ / Python 
* GUI debug
* Online judge testcases downloading and testing. (based on online-judge-tools)
* Debug with online judge testcases
* Do online judge submission
* Completer and jumper (based on racer) 
* Auto Formatting (based on rustfmt)
* Rust REPL (based on evcxr_repl)
* Live Templates (IntelliJ style)
* Contest Task Browsing
* Display graph structure

Software Requirements
==============================
* Linux OS (I only tested with Ubuntu 16.04 / 18.04)
* Python (3.5 or later)

If you want to develop with rust-lang, you need
* evcxr_repl (`cargo install evcxr_repl`)
* rustfmt(`rustup component add rustfmt`)
* racer(Please see https://github.com/racer-rust/racer)

If you want to develop with C++, you need
* clang (8.0.0 or later)
* clang-format
* g++

If you want to develop with Python 3.x, you need
* jedi (`pip install jedi`)
* autopep8 (`pip install autopep8`)

Usage
==============================
If you want to use Rujaion please read and agree with our [cookie policy](#policy).

### Install to Linux

Install Qt5. If you use Ubuntu 16.04,

```bash
$ apt update && apt install -y qt5-default libxcb-xinerama0-dev libnss3 libasound2
```
will work. Or please see official document (https://www.qt.io/download). 

Install Rujaion

```bash
$ pip3 install Rujaion
$ rujaion
```

### Use on Docker
See https://github.com/fukatani/rust-gui-debugger/blob/master/docker/Readme.md

KeyBinds
==============================
- Open File (Ctrl + o)
- Save File (Ctrl + s)
- Delete current line (Ctrl + k)
- Set or unset brake point (F5)
- Start Debug or continue (F9)
- Start Debug with downloaded testcase (F4)
- Download sample testcases (Input url in browser and Press Enter)
- Focus on URL (F6)
- Run (Ctrl + F9)
- Next (F8)
- Step in (F7)
- Step out (Shift + F8)
- Go to definition (Ctrl + b)
- Go to first compile error (F2)
- Terminate debug process (Esc)
- display value (editting display widget "Name" columns)
- Comment out (Ctrl + /)
- Toggle Show / Hide Browser Widget (F12)
- Toggle Full Screen Browsing / or not (Ctrl + F12)
- Toggle Show / Hide Console Widget (F11)

Contest Task Browsing
==============================
![browse](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/browse.png)

You can browse contest task by Browser Widget.
You can hide (or show) browser, press F11 key.
If page URL is contest task page, contest task is downloaded automatically by online-judge-tools.

Login to Programming Contest
==============================

Some online-judge-tools features (ex. submit) needs login session information.

You can login by
1) Login with Browser Widget
2) Tool bar -> Contest -> Login

<a name="policy">Cookie and Security Policy</a>
==============================

Rujaion only use cookies for programming contest pages which is supported by [online-judge-tools](https://github.com/kmyk/online-judge-tools).

Though you can access any page by browser widget, cookies in other page will not be handled in rujaion explicitly. (QtWebEngine may use it.)

Cookies are only used for online-judge-tools features that require login. (Excepts QtWebEngine inner use.)

We are not liable for damages arising from any user with using rujaion.

Display Graph (Powered by Graph x Graph)
==============================

In contest, you often draw graph structure.

Select graph elements and do "View Graph" in browser right click menu, you can draw graph structure easily.

![screen_cast_graph](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/graph_view.gif)

Blog Entry
==============================
https://codeforces.com/blog/entry/69975
