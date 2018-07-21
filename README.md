Rust GUI Debugger
==============================

![screen_shot](https://github.com/fukatani/rust-gui-debugger/blob/master/doc/debug.png)

Introduction
==============================
Lightweight rust GUI Debugger based on PyQt and rust-gdb.

Not only debugging, editting text file is supported.

Current version is alpha, some function is not implemented. 

Support one file project only.

Software Requirements
==============================
* Python (3.4 or later)
* PyQt5
* pexpect

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
- Terminate debug process (Esc)
- Set break point (double click on text)
- display value (editting display widget "Name" columns)
