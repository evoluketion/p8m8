# p8m8

A lightweight, custom-built code editor for [PICO-8](https://www.pico-8.com/) Lua cartridges, built with PyQt6.

## Features

- **Tabbed editing** — Opening a `.p8` cartridge splits its Lua source on `-->8` markers into separate tabs, mirroring PICO-8's own multi-tab code editor. New tabs can be added with the `+` tab.
- **Token counter** — Tracks a live token count against PICO-8's 8192-token cartridge limit, using a Lua-aware tokenizer (comments, strings, operators, and free tokens like `end`/`local` are handled the way PICO-8 counts them).
- **Line counter** — Shows the current line and total line count for the active tab.
- **Cartridge I/O** — Open an existing `.p8` cartridge (parses the `__lua__`, `__gfx__`, `__label__`, `__gff__`, `__map__`, and `__sfx__` sections) and save your edited Lua back out as a `.p8` file.
- **Editor preferences** — Toggle visible tabs/spaces and line wrapping from the View menu; preferences persist to `prefs.json`.
- **Custom frameless window** — A borderless window with its own titlebar controls (minimize, maximize/restore, close) and a PICO-8-styled font/theme.

## Requirements

- Python 3
- [PyQt6](https://pypi.org/project/PyQt6/)

```bash
pip install PyQt6
```

## Running

```bash
python App.py
```

## Project structure

```
App.py                     # Application entry point / main window
components/
  Editor.py                 # Text editor widget + PICO-8 token counting
  TabWidget.py               # Tab management, cartridge (de)serialization
  MainToolbar.py             # Custom titlebar, menu bar, file open/save
  Footer.py                  # Status bar (line / token counts)
  LineNumberArea.py          # Gutter line numbers
config/
  prefs.py                   # Persisted user preferences (prefs.json)
styles/
  style.qss                  # Application stylesheet
assets/
  fonts/pico-8.otf            # PICO-8 font
```

## Status

Early-stage / work in progress. `new` and `save` (in-place) menu actions are not yet implemented — use `open` and `save as` for now.
