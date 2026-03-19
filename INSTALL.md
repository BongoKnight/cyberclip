# CyberClip Installation Guide

## Recommended Installation (with uv)

[uv](https://github.com/astral-sh/uv) is the recommended way to install CyberClip. It's faster and handles dependencies better.

### Basic Installation

Install CyberClip with core TUI (Terminal User Interface) features:

```bash
uv tool install git+https://github.com/BongoKnight/cyberclip
```

This includes the main clipboard parser, all actions, and the Textual-based TUI interface.

### Alternative: pip Installation

You can also install with pip:

```bash
pip install cyberclip
```

## Optional Features

### GUI - Vertical Menu (Qt-based)

The vertical menu provides a visual menu triggered with `Ctrl+Alt+M`. This feature is **Windows-focused** and requires Qt dependencies.

**With uv:**
```bash
uv tool install "git+https://github.com/BongoKnight/cyberclip[gui]"
```

**With pip:**
```bash
pip install cyberclip[gui]
```

**Dependencies added:**
- PyQt5 - Qt5 GUI framework
- keyboard - Global hotkey support
- win11toast - Toast notifications (Windows only)

**Note for Linux users:** While the menu can work on Linux, toast notifications will fall back to console output.

### Web Interface (Flask-based)

The web interface provides a browser-based UI for CyberClip.

**With uv:**
```bash
uv tool install "git+https://github.com/BongoKnight/cyberclip[web]"
```

**With pip:**
```bash
pip install cyberclip[web]
```

**Dependencies added:**
- Flask - Web framework
- textual_serve - Textual web serving

### All Optional Features

Install everything:

**With uv:**
```bash
uv tool install "git+https://github.com/BongoKnight/cyberclip[all]"
```

**With pip:**
```bash
pip install cyberclip[all]
```

## Platform-Specific Notes

### Windows
All features are fully supported. Platform-specific dependencies (pywin32, win11toast) are automatically installed.

### Linux
- Core TUI features work perfectly
- Vertical menu GUI works but notifications fall back to console
- Web interface works perfectly

### macOS
- Core TUI features work perfectly
- Vertical menu GUI may require additional Qt dependencies
- Web interface works perfectly

## Minimal Installation for Servers

If you're installing on a headless server or CI/CD environment and only need the parsing capabilities:

**With uv:**
```bash
uv pip install --no-deps git+https://github.com/BongoKnight/cyberclip
# Then install only the dependencies you need
```

**With pip:**
```bash
pip install cyberclip --no-deps
pip install <only the dependencies you need>
```

## Development Installation

### With uv (recommended)

```bash
git clone https://github.com/BongoKnight/cyberclip.git
cd cyberclip
uv pip install -e .[all]
```

### With pip

```bash
git clone https://github.com/BongoKnight/cyberclip.git
cd cyberclip
pip install -e .[all]
```

## Trying CyberClip (Temporary Run)

You can try CyberClip without installing it:

```bash
uv tool run git+https://github.com/BongoKnight/cyberclip
```
