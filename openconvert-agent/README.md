# OpenConvert Agent

A local-first, open-source file conversion assistant for macOS. The MVP includes:
- A small desktop UI (PySide6) for selecting files and target formats.
- A safe conversion engine for common image conversions (Pillow).
- Optional document-to-PDF conversion using a locally installed LibreOffice.
- A command-line interface suitable for macOS Finder Quick Actions.
- An optional Ollama-backed intent helper that only proposes a supported conversion; it never executes arbitrary commands.

## Design principles
- Files remain on the Mac. No upload, account, telemetry, or cloud API.
- Original files are never modified.
- Existing outputs are never overwritten; the engine chooses `name (1).ext`, `name (2).ext`, etc.
- The AI helper is optional and cannot run shell commands.
- Only explicitly supported conversion recipes are available.

## MVP support
- Images: PNG, JPEG, WEBP, BMP, TIFF (Pillow-supported formats).
- Documents to PDF: common office documents supported by the local LibreOffice installation.
- More formats should be added as explicit, tested recipes rather than arbitrary extension changes.

## Requirements
- macOS 13+ recommended
- Python 3.11+
- For image conversion: Pillow
- For desktop UI: PySide6
- For DOC/DOCX/ODT/RTF/TXT/HTML-to-PDF: LibreOffice installed locally and `soffice` available on PATH
- Optional AI: Ollama running locally, with a model pulled (for example `llama3.2:3b`)

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[ui]"
openconvert --help
openconvert gui
```

Convert an image:
```bash
openconvert convert ./photo.png --to webp
```

Convert a document to PDF (requires LibreOffice):
```bash
openconvert convert ./report.docx --to pdf
```

Ask the optional local intent helper:
```bash
openconvert plan "convert photo.png to webp"
```

Run tests:
```bash
pip install -e ".[dev]"
pytest
```

## macOS Finder Quick Action
See `macos/README.md`. The provided shell script is designed to receive one or more selected file paths from an Automator Quick Action. It opens a local notification and converts to PDF for supported documents or WEBP for images by default. You can edit the target mapping or use the desktop UI for explicit target selection.

For a production release, package this as a signed/notarized app and provide a native Finder extension or carefully maintained Quick Action installer. The script is an MVP integration, not a signed installer.

## Security notes
- Treat user-selected files as untrusted input.
- Do not run conversion tools on files from privileged locations without user intent.
- Conversion subprocesses use argument arrays (not shell strings), timeouts, and a restricted output directory.
- This MVP does not recursively scan folders or delete source files.
- LibreOffice and other external tools have their own security and licensing considerations.
- Review all dependency licenses and packaging obligations before redistribution.

## Project layout
```
src/openconvert/
  __init__.py
  cli.py
  engine.py
  planner.py
  gui.py
macos/
  finder_quick_action.sh
  README.md
tests/
  test_engine.py
```

## License
MIT for this project scaffold. Third-party tools and dependencies retain their own licenses.
