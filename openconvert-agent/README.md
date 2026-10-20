# OpenConvert Agent

A local-first, open-source file conversion assistant for macOS. The MVP includes:
- A small desktop UI (PySide6) for selecting files and target formats.
- A safe conversion engine for common image conversions (Pillow).
- PDF-to-image conversion, image-to-PDF, PDF merge/split/compression, and local PDF text export to DOCX, XLSX, PPTX, or TXT.
- Optional office/document-to-PDF conversion using a locally installed LibreOffice.
- A command-line interface suitable for macOS Finder Quick Actions.
- An optional Ollama-backed intent helper that only proposes a supported conversion; it never executes arbitrary commands.

## Design principles
- Files remain on the Mac. No upload, account, telemetry, or cloud API.
- Original files are never modified.
- Existing outputs are never overwritten; the engine chooses `name (1).ext`, `name (2).ext`, etc.
- The AI helper is optional and cannot run shell commands.
- Only explicitly supported conversion recipes are available.

## MVP support
- Images: PNG, JPEG, WEBP, BMP, TIFF, and GIF input (Pillow-supported formats).
- Images to PDF: convert one image or combine selected images in order into one PDF.
- PDFs: export pages to PNG/JPEG, extract selectable text to DOCX/XLSX/PPTX/TXT, merge, split into single-page files, and optimize by recompressing streams.
- Documents to PDF: common office, spreadsheet, presentation, and text formats supported by the local LibreOffice installation.
- More formats should be added as explicit, tested recipes rather than arbitrary extension changes.

## Requirements
- macOS 13+ recommended
- Python 3.11+
- For image and PDF conversions: Pillow, PyMuPDF, python-docx, openpyxl, python-pptx
- For desktop UI: PySide6
- For office/document-to-PDF: LibreOffice installed locally and `soffice` available on PATH
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

### Desktop launcher
From the repo root, you can also launch the desktop app with the bundled scripts:
```bash
chmod +x desktop/openconvert-launcher.sh
./desktop/openconvert-launcher.sh
```

To install a desktop entry for your Linux session:
```bash
chmod +x desktop/install_desktop_entry.sh
./desktop/install_desktop_entry.sh
```

This creates a `.desktop` shortcut under `~/.local/share/applications` that launches the app from the project directory.

To build a downloadable Linux desktop bundle:
```bash
chmod +x desktop/build_linux_bundle.sh
./desktop/build_linux_bundle.sh
```

This produces a zip archive in `dist/openconvert-agent-desktop.zip`.

### macOS bundle scaffold
A minimal macOS `.app` bundle is included under `macos/OpenConvert Agent.app` for local app-style launching.

```bash
open "macos/OpenConvert Agent.app"
```

This is a lightweight launcher scaffold and is not a notarized shipping build.

### Browser extension wrapper
A minimal browser extension wrapper is available under `extension/` for a launcher helper experience.

See `extension/README.md` for loading instructions in Chrome/Edge.

Convert an image:
```bash
openconvert convert ./photo.png --to webp
```

Convert a document to PDF (requires LibreOffice):
```bash
openconvert convert ./report.docx --to pdf
```

Convert a PDF to images or editable text formats:
```bash
openconvert convert ./report.pdf --to png
openconvert convert ./report.pdf --to docx
openconvert convert ./report.pdf --to xlsx
```

Merge, split, or optimize PDFs:
```bash
openconvert merge-pdf ./first.pdf ./second.pdf
openconvert split-pdf ./report.pdf
openconvert compress-pdf ./report.pdf
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
- PDF-to-Office exports extract selectable text and do not preserve the original page layout; scanned PDFs need OCR, which is not included. PDF recompression may not reduce every file's size.
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
desktop/
  openconvert-launcher.sh
  openconvert-agent.desktop
  install_desktop_entry.sh
  uninstall_desktop_entry.sh
  build_linux_bundle.sh
extension/
  manifest.json
  popup.html
  popup.js
  README.md
macos/
  finder_quick_action.sh
  README.md
  OpenConvert Agent.app/
    Contents/
      Info.plist
      MacOS/
        openconvert-launcher
tests/
  test_engine.py
```

## License
MIT for this project scaffold. Third-party tools and dependencies retain their own licenses.
