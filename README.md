Online judge aware Rust IDE
==============================

![screen_shot](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/debug.png)

Introduction
==============================
Lightweight rust GUI Debugger based on PyQt and rust-gdb.

Current version is alpha, some function is not implemented. 

Support one file project only.

Feature
==============================
* GUI debug
* completer and jumper (based on racer) 
* Online judge testcases downloading and testing. (based on online-judge-tools)
* Debug with online judge testcases
* Do online judge submission

Software Requirements
==============================
* Python (3.4 or later)
* PyQt5
* pexpect
* online-judge-tools (0.1.36 or later)
* rustfmt
* racer


Usage
==============================

```bash
git clone https://github.com/fukatani/rust-gui-debugger.git
cd rust-gui-debugger/src
python3 ./rust_debugger.py
```

KeyBinds
==============================
- Open File (Ctrl + o)
- Save File (Ctrl + s)
- Start Debug or continue (F9)
- Run (Ctrl + F9)
- Next (F8)
- Step in (F7)
- Step out (Shift + F8)
- Jump to definition (F2)
- Terminate debug process (Esc)
- Set break point (double click on text)
- display value (editting display widget "Name" columns)
