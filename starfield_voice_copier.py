import sys
import shutil
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QProgressBar,
    QTextEdit, QFileDialog, QMessageBox
)

# Language mapping from the original Inno Setup script
LANG_MAP = {
    "English": "en",
    "German": "de",
    "French": "fr",
    "Italian": "it",
    "Spanish": "es",
    "Polish": "pl",
    "Portuguese": "pt",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh",
}

# File patterns to copy (same as in the original .iss file)
def get_patterns(lang_code: str):
    return [
        f"*Voices_{lang_code}.ba2",
        f"*Voices_{lang_code}_*.ba2",
        f"*voices_{lang_code}.ba2",
        f"*voices_{lang_code}_*.ba2",
        "*.esm",
    ]


class CopyWorker(QThread):
    """Worker thread that performs the copying and emits progress signals."""
    progress = Signal(int, str)      # percentage, text
    finished = Signal(bool, str)     # success, message

    def __init__(self, src: Path, dst: Path, lang_code: str):
        super().__init__()
        self.src = src
        self.dst = dst
        self.lang_code = lang_code
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            self.dst.mkdir(parents=True, exist_ok=True)

            # 1) Collect all files to copy
            files_to_copy = []
            for pattern in get_patterns(self.lang_code):
                for f in self.src.glob(pattern):
                    if f.is_file():
                        files_to_copy.append(f)

            if not files_to_copy:
                self.finished.emit(False, "No files found to copy for the selected language.")
                return

            total = len(files_to_copy)
            copied = 0

            # 2) Copying with progress bar updates
            for src_file in files_to_copy:
                if self._cancelled:
                    self.finished.emit(False, "Copying was cancelled.")
                    return

                dst_file = self.dst / src_file.name
                shutil.copy2(src_file, dst_file)

                copied += 1
                percent = int(copied / total * 100)
                self.progress.emit(percent, f"Copying {src_file.name} ({copied}/{total})")

            self.finished.emit(True, f"Successfully copied {copied} files for language {self.lang_code.upper()}.")

        except Exception as e:
            self.finished.emit(False, f"Error during copying: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Starfield Voice & Core Files Copier")
        self.setMinimumSize(650, 520)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(LANG_MAP.keys())
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Source folder
        src_layout = QHBoxLayout()
        src_layout.addWidget(QLabel("Source Data Folder:"))
        self.src_edit = QLineEdit()
        src_layout.addWidget(self.src_edit)
        src_btn = QPushButton("Browse...")
        src_btn.clicked.connect(self.browse_src)
        src_layout.addWidget(src_btn)
        layout.addLayout(src_layout)

        # Destination folder
        dst_layout = QHBoxLayout()
        dst_layout.addWidget(QLabel("Destination Data Folder:"))
        self.dst_edit = QLineEdit()
        dst_layout.addWidget(self.dst_edit)
        dst_btn = QPushButton("Browse...")
        dst_btn.clicked.connect(self.browse_dst)
        dst_layout.addWidget(dst_btn)
        layout.addLayout(dst_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

        # Copy button
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.start_copy)
        layout.addWidget(self.copy_btn)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.worker = None

    def browse_src(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Data Folder")
        if folder:
            self.src_edit.setText(folder)

    def browse_dst(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Data Folder")
        if folder:
            self.dst_edit.setText(folder)

    def start_copy(self):
        src = Path(self.src_edit.text().strip())
        dst = Path(self.dst_edit.text().strip())
        lang = self.lang_combo.currentText()
        lang_code = LANG_MAP[lang]

        if not src.is_dir():
            QMessageBox.warning(self, "Error", "Source folder does not exist.")
            return
        if not dst.is_dir():
            QMessageBox.warning(self, "Error", "Destination folder does not exist.")
            return

        # Optional check if destination contains "data" (similar to the .iss script)
        if "data" not in str(dst).lower():
            reply = QMessageBox.question(
                self, "Warning",
                "The destination folder does not contain the word 'Data'. Do you really want to continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        self.copy_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log.clear()
        self.log.append(f"Starting copy for language: {lang} ({lang_code})")

        self.worker = CopyWorker(src, dst, lang_code)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_progress(self, percent: int, text: str):
        self.progress_bar.setValue(percent)
        self.status_label.setText(text)

    def on_finished(self, success: bool, message: str):
        self.copy_btn.setEnabled(True)
        self.status_label.setText(message)
        self.log.append(message)
        if success:
            QMessageBox.information(self, "Done", message)
        else:
            QMessageBox.warning(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())