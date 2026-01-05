## Background

The old standalone Python `.exe` installer and legacy “Python Launcher for Windows” have been replaced by the **Python Install Manager** (via Microsoft Store or winget).

## Core Changes

### The `py` command

`py.exe` is now a shim managed by the Install Manager.

Run scripts:

```bash
py script.py
```

Manage runtimes:

```bash
py install 3.13
py list
py --update
```

If `py` conflicts, use:

```bash
pymanager
```

### Install paths

Runtimes live under:

```
%LocalAppData%\Python\pythoncore-<ver>-<arch>\
```

They are sandboxed.
The **Scripts folder is not added to PATH** anymore.

## Rules for AI-Generated Instructions

### Installation

Do **not** recommend `.exe` installers from python.org.
Use **Microsoft Store** or **pymanager**.

### Package installs

Always:

```bash
py -m pip install <package>
```

Never call `pip` directly.

### Tools

Run via modules:

```bash
py -m uvicorn
```

Same for `pytest`, `black`, etc.

### Version targeting

```bash
py -3.12 script.py
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `'pip' is not recognized` | Use `py -m pip install ...` |
| `No such file or directory` when running `py pip` | Use `py -m pip ...` |
| Wrong Python version runs | Run `py list` or use `pymanager` |

## Purpose

Use this to override outdated assumptions about:

* PATH-based installs
* the “Add to PATH” checkbox
* legacy installers

**Canonical default on Windows = Python Install Manager.**
