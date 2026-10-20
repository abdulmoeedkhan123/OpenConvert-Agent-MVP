from __future__ import annotations
import os
import sys
from pathlib import Path

if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QComboBox, QMessageBox, QProgressBar
)

from .engine import (
    IMAGE_EXTENSIONS, PDF_EXTENSIONS, compress_pdf, convert, convert_images_to_pdf,
    merge_pdfs, split_pdf, supported_targets, ConversionError,
)

def _qt_message_handler(message_type, context, message):
    if message == "This plugin does not support propagateSizeHints()":
        return
    sys.stderr.write(f"Qt {message_type.name}: {message}\n")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenConvert Agent")
        self.resize(720, 480)
        self.files: list[Path] = []
        root = QWidget()
        layout = QVBoxLayout(root)
        intro = QLabel("Local file conversion. Originals are preserved and outputs are never overwritten.")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        buttons = QHBoxLayout()
        add_button = QPushButton("Add files…")
        add_button.clicked.connect(self.add_files)
        remove_button = QPushButton("Remove selected")
        remove_button.clicked.connect(self.remove_selected)
        buttons.addWidget(add_button)
        buttons.addWidget(remove_button)
        layout.addLayout(buttons)

        self.list_widget = QListWidget()
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setToolTip("Use Add files to select files. Drag-and-drop can be enabled in a later UI iteration.")
        layout.addWidget(self.list_widget)

        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Convert selected files to:"))
        self.target = QComboBox()
        self.target.addItems([
            "pdf", "png", "jpg", "jpeg", "webp", "bmp", "tiff",
            "docx", "xlsx", "pptx", "txt",
            "merge-pdf", "split-pdf", "compress-pdf",
        ])
        target_row.addWidget(self.target)
        layout.addLayout(target_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.status = QLabel("Ready")
        layout.addWidget(self.status)

        convert_button = QPushButton("Convert…")
        convert_button.clicked.connect(self.convert_selected)
        layout.addWidget(convert_button)
        self.setCentralWidget(root)

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Choose files")
        for raw in paths:
            path = Path(raw).resolve()
            if path not in self.files:
                self.files.append(path)
                self.list_widget.addItem(str(path))

    def remove_selected(self):
        indices = sorted({self.list_widget.row(item) for item in self.list_widget.selectedItems()}, reverse=True)
        for index in indices:
            self.files.pop(index)
            self.list_widget.takeItem(index)

    def convert_selected(self):
        selected_indices = sorted({self.list_widget.row(item) for item in self.list_widget.selectedItems()})
        chosen = [self.files[i] for i in selected_indices] if selected_indices else list(self.files)
        if not chosen:
            QMessageBox.information(self, "No files", "Add files first.")
            return
        target = self.target.currentText()
        if target == "merge-pdf":
            if len(chosen) < 2 or any(path.suffix.lower() not in PDF_EXTENSIONS for path in chosen):
                QMessageBox.warning(self, "Select PDFs", "Choose at least two PDF files to merge.")
                return
            self._run_pdf_action("Merge PDFs", lambda: [merge_pdfs(chosen)])
            return
        if target == "split-pdf":
            if any(path.suffix.lower() not in PDF_EXTENSIONS for path in chosen):
                QMessageBox.warning(self, "Select PDFs", "Choose PDF files to split.")
                return
            self._run_pdf_action(
                "Split PDFs", lambda: [output for path in chosen for output in split_pdf(path)]
            )
            return
        if target == "compress-pdf":
            if any(path.suffix.lower() not in PDF_EXTENSIONS for path in chosen):
                QMessageBox.warning(self, "Select PDFs", "Choose PDF files to compress.")
                return
            self._run_pdf_action(
                "Compress PDFs", lambda: [compress_pdf(path) for path in chosen]
            )
            return
        if target == "pdf" and len(chosen) > 1 and all(
            path.suffix.lower() in IMAGE_EXTENSIONS for path in chosen
        ):
            self._run_pdf_action(
                "Create PDF", lambda: [convert_images_to_pdf(chosen)]
            )
            return
        incompatible = [p.name for p in chosen if target not in supported_targets(p)]
        if incompatible:
            QMessageBox.warning(
                self, "Unsupported conversion",
                "The following files do not support this target in the MVP:\n\n" + "\n".join(incompatible)
            )
            return
        confirm = QMessageBox.question(
            self, "Confirm conversion",
            f"Convert {len(chosen)} file(s) to {target.upper()}?\n\n"
            "Originals will be preserved. Existing outputs will not be overwritten.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        errors, successes = [], []
        self.progress.setRange(0, len(chosen))
        self.progress.setValue(0)
        for index, path in enumerate(chosen, 1):
            try:
                outputs = convert(path, target)
                if not isinstance(outputs, list):
                    outputs = [outputs]
                successes.extend(f"{path.name} → {out.name}" for out in outputs)
            except ConversionError as exc:
                errors.append(f"{path.name}: {exc}")
            self.progress.setValue(index)
            QApplication.processEvents()

        self.status.setText(f"Finished: {len(successes)} succeeded, {len(errors)} failed.")
        summary = "\n".join(successes + ([""] if successes and errors else []) + errors)
        QMessageBox.information(self, "Conversion results", summary or "No output.")

    def _run_pdf_action(self, title, action):
        try:
            outputs = action()
        except ConversionError as exc:
            QMessageBox.warning(self, title, str(exc))
            return
        self.status.setText(f"Finished: {len(outputs)} output file(s) created.")
        QMessageBox.information(self, title, "\n".join(str(path) for path in outputs))

def run_gui() -> int:
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        qInstallMessageHandler(_qt_message_handler)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
