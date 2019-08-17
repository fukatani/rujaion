Online judge aware Rust / C++ IDE
==============================
<a href="https://github.com/ambv/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

[![Travis](https://img.shields.io/travis/fukatani/rujaion.svg)](https://travis-ci.org/fukatani/rujaion)

![screen_cast](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/rujaion.gif)

Introduction
==============================
Lightweight Rust IDE based on PyQt. (C++ feature is experimental)

Current version is alpha, some function is not implemented. 

Support one file project only.

Feature
==============================
* Rust / C++ (If you opened *.cpp file, rujaion handles it as C++ source file. Otherwise, handles as Rust) 
* GUI debug
* Online judge testcases downloading and testing. (based on online-judge-tools)
* Debug with online judge testcases
* Do online judge submission
* Completer and jumper (based on racer) 
* Auto Formatting (based on rustfmt)
* Rust REPL (based on evcxr_repl)
* Live Templates (IntelliJ style)
* Contest Task Browsing

Software Requirements
==============================
* Python (3.5 or later)
* PyQt5 (`sudo apt install pyqt5`)
* PyQtWebEngine
* pexpect 
* online-judge-tools (6.6.0 or later)
* evcxr_repl (`cargo install evcxr_repl`)
* rustfmt
* racer

If you want to use C++, in addition, you need
* clang (8.0.0 or later)
* clang-format
* g++

Usage
==============================

If you want to use rujaion please read and agree with our [cookie policy](#policy).

```bash
$ git clone https://github.com/fukatani/rujaion.git
$ cd rujaion
$ python3 setup.py install
$ rujaion_main.py
```

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
- Jump to definition (F2)
- Terminate debug process (Esc)
- display value (editting display widget "Name" columns)
- Comment out (Ctrl + /)
- Toggle Show / Hide Browser Widget (F12)
- Toggle Full Screen Browsing / or not (Ctrl + F12)
- Toggle Show / Hide Console Widget (F11)

Contest Task Browsing
==============================
![browse](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/browse.png)

You can browse contest task by Dock Browser Widget.
You can hide (or show) browser, press F11 key.
If page URL is contest task page, contest task is downloaded automatically by online-judge-tools.

Login to Programming Contest
==============================

Some online-judge-tools features (ex. submit) needs login session information.

You can login by
1) Login Browser Widget
2) Tool bar -> Contest -> Login

<a name="policy">Cookie and Security Policy</a>
==============================

Rujaion only use cookies for programming contest pages which is supported by [online-judge-tools](https://github.com/kmyk/online-judge-tools).

Though you can access any page by browser widget, cookies in other page will not be handled in rujaion explicitly. (QtWebEngine may use it.)

Cookies are only used for online-judge-tools features that require login. (Excepts QtWebEngine inner use.)

We are not liable for damages arising from any user with using rujaion.
