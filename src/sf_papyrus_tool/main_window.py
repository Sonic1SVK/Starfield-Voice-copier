from pathlib import Path

from PySide6.QtCore import Qt, QSettings, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QTextEdit, QComboBox, QGroupBox,
    QFileDialog, QMessageBox, QCheckBox, QProgressBar, QSplitter,
    QStatusBar,
)

from .config import ToolConfig
from .workers import DecompileWorker, CompileWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Starfield Papyrus Tool")
        self.resize(980, 760)

        self.config = ToolConfig()
        self.qs = QSettings("SFPapyrusTool", "SFPapyrusTool")
        self.config.load(self.qs)

        self._selected_files: list[Path] = [] # Uchováva viacero vybraných súborov

        self._build_ui()
        self._apply_config()

        self.worker: DecompileWorker | CompileWorker | None = None

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        splitter = QSplitter(Qt.Vertical)

        # ---- Top: settings + actions ----
        top = QWidget()
        top_layout = QVBoxLayout(top)

        # Tool paths
        tools_group = QGroupBox("Tool paths")
        tools_form = QFormLayout(tools_group)

        self.champollion_edit = QLineEdit()
        self.champollion_edit.setPlaceholderText("Path to Champollion.exe / champollion")
        tools_form.addRow(
            "Champollion:",
            self._with_browse(self.champollion_edit, self._browse_champollion),
        )

        self.compiler_edit = QLineEdit()
        self.compiler_edit.setPlaceholderText("Path to Caprica.exe / PapyrusCompiler.exe")
        tools_form.addRow(
            "Compiler:",
            self._with_browse(self.compiler_edit, self._browse_compiler),
        )

        self.compiler_type_combo = QComboBox()
        self.compiler_type_combo.addItem("Caprica (recommended, MIT)", "caprica")
        self.compiler_type_combo.addItem("PapyrusCompiler (Creation Kit)", "papyrus")
        tools_form.addRow("Compiler type:", self.compiler_type_combo)

        self.import_dir_edit = QLineEdit()
        self.import_dir_edit.setPlaceholderText("Directory with extracted vanilla .psc sources")
        tools_form.addRow(
            "Import dir:",
            self._with_browse_dir(self.import_dir_edit),
        )

        self.game_combo = QComboBox()
        for name, code in [("Starfield", "starfield"), ("Skyrim SE", "skyrim"), ("Fallout 4", "fo4")]:
            self.game_combo.addItem(name, code)
        tools_form.addRow("Game:", self.game_combo)

        self.postprocess_check = QCheckBox("Run Starfield post-processing on decompiled output")
        self.postprocess_check.setChecked(True)
        tools_form.addRow("", self.postprocess_check)

        top_layout.addWidget(tools_group)

        # Files & Modes
        files_group = QGroupBox("Files / Batch Processing")
        files_form = QFormLayout(files_group)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Jeden súbor (Single File)", "Viacero súborov (Multiple Files)", "Celý priečinok (Whole Directory)"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        files_form.addRow("Režim (Mode):", self.mode_combo)

        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Vyber .pex / .psc súbor alebo priečinok")
        files_form.addRow("Zdroj (Source):", self._with_browse(self.source_edit, self._browse_source))

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Výstupný priečinok")
        files_form.addRow("Cieľ (Output dir):", self._with_browse_dir(self.output_edit))

        top_layout.addWidget(files_group)

        # Actions
        actions = QHBoxLayout()
        self.btn_decompile = QPushButton("⬇  Decompile .pex → .psc")
        self.btn_compile = QPushButton("⬆  Compile .psc → .pex")
        self.btn_decompile.clicked.connect(self.on_decompile)
        self.btn_compile.clicked.connect(self.on_compile)
        actions.addWidget(self.btn_decompile)
        actions.addWidget(self.btn_compile)
        actions.addStretch()
        top_layout.addLayout(actions)

        splitter.addWidget(top)

        # ---- Bottom: log ----
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)

        log_header = QHBoxLayout()
        log_header.addWidget(QLabel("Log:"))
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(lambda: self.log.clear())
        log_header.addWidget(btn_clear)
        log_header.addStretch()
        log_layout.addLayout(log_header)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 10))
        self.log.setPlaceholderText("Output from tools will appear here…")
        log_layout.addWidget(self.log)

        splitter.addWidget(log_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedWidth(120)
        self.progress.hide()
        self.status.addPermanentWidget(self.progress)
        self.status.showMessage("Ready")

    def _with_browse(self, edit: QLineEdit, callback) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(edit, 1)
        btn = QPushButton("…")
        btn.setFixedWidth(32)
        btn.clicked.connect(callback)
        h.addWidget(btn)
        return w

    def _with_browse_dir(self, edit: QLineEdit) -> QWidget:
        def browse() -> None:
            path = QFileDialog.getExistingDirectory(self, "Select directory")
            if path:
                edit.setText(path)
        return self._with_browse(edit, browse)

    def _browse_champollion(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Champollion executable")
        if path: self.champollion_edit.setText(path)

    def _browse_compiler(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select compiler executable")
        if path: self.compiler_edit.setText(path)

    def _on_mode_changed(self) -> None:
        self.source_edit.clear()
        self._selected_files.clear()
        mode = self.mode_combo.currentIndex()
        if mode == 0:
            self.source_edit.setPlaceholderText("Vyber jeden .pex / .psc súbor")
        elif mode == 1:
            self.source_edit.setPlaceholderText("Vyber viacero súborov (Ctrl+klik)")
        else:
            self.source_edit.setPlaceholderText("Vyber celý priečinok so skriptami")

    def _browse_source(self) -> None:
        mode = self.mode_combo.currentIndex()

        if mode == 0: # Jeden súbor
            path, _ = QFileDialog.getOpenFileName(self, "Select file", filter="Papyrus (*.pex *.psc)")
            if path:
                self.source_edit.setText(path)
                self._selected_files = [Path(path)]

        elif mode == 1: # Viacero súborov
            paths, _ = QFileDialog.getOpenFileNames(self, "Select files", filter="Papyrus (*.pex *.psc)")
            if paths:
                self.source_edit.setText(f"Vybraných súborov: {len(paths)}")
                self._selected_files = [Path(p) for p in paths]

        else: # Celý priečinok
            path = QFileDialog.getExistingDirectory(self, "Select directory")
            if path:
                self.source_edit.setText(path)
                self._selected_files = [] # naplní sa pri spustení

    def _apply_config(self) -> None:
        self.champollion_edit.setText(self.config.champollion)
        self.compiler_edit.setText(self.config.compiler)
        idx = self.compiler_type_combo.findData(self.config.compiler_type)
        if idx >= 0: self.compiler_type_combo.setCurrentIndex(idx)
        self.import_dir_edit.setText(self.config.import_dir)
        idx = self.game_combo.findData(self.config.game)
        if idx >= 0: self.game_combo.setCurrentIndex(idx)
        self.postprocess_check.setChecked(self.config.postprocess)

    def _read_config(self) -> None:
        self.config.champollion = self.champollion_edit.text().strip()
        self.config.compiler = self.compiler_edit.text().strip()
        self.config.compiler_type = self.compiler_type_combo.currentData()
        self.config.import_dir = self.import_dir_edit.text().strip()
        self.config.game = self.game_combo.currentData()
        self.config.postprocess = self.postprocess_check.isChecked()
        self.config.save(self.qs)

    def _get_files_to_process(self, ext: str) -> list[Path]:
        mode = self.mode_combo.currentIndex()
        if mode == 0 or mode == 1:
            return [f for f in self._selected_files if f.suffix.lower() == ext]
        else:
            src = Path(self.source_edit.text().strip())
            if src.is_dir():
                return list(src.glob(f"*{ext}"))
        return []

    @Slot()
    def on_decompile(self) -> None:
        self._read_config()
        out_text = self.output_edit.text().strip()
        if not out_text or not Path(out_text).is_dir():
            QMessageBox.warning(self, "Chyba", "Vyber platný výstupný priečinok.")
            return

        files = self._get_files_to_process(".pex")
        if not files:
            QMessageBox.warning(self, "Chyba", "Nenašli sa žiadne .pex súbory na dekompiláciu.")
            return

        self._start_worker(DecompileWorker(
            champollion=self.config.champollion,
            files=files,
            out_dir=Path(out_text),
            postprocess=self.config.postprocess,
        ))

    @Slot()
    def on_compile(self) -> None:
        self._read_config()
        out_text = self.output_edit.text().strip()
        if not out_text or not Path(out_text).is_dir():
            QMessageBox.warning(self, "Chyba", "Vyber platný výstupný priečinok.")
            return

        files = self._get_files_to_process(".psc")
        if not files:
            QMessageBox.warning(self, "Chyba", "Nenašli sa žiadne .psc súbory na kompiláciu.")
            return

        self._start_worker(CompileWorker(
            compiler=self.config.compiler,
            compiler_type=self.config.compiler_type,
            files=files,
            out_dir=Path(out_text),
            import_dir=self.config.import_dir,
            game=self.config.game,
        ))

    def _start_worker(self, worker) -> None:
        self.worker = worker
        worker.log.connect(self.log.append)
        worker.finished.connect(self._on_worker_done)
        self.btn_decompile.setEnabled(False)
        self.btn_compile.setEnabled(False)
        self.progress.show()
        self.status.showMessage("Spracováva sa...")
        worker.start()

    def _on_worker_done(self, ok: bool) -> None:
        self.btn_decompile.setEnabled(True)
        self.btn_compile.setEnabled(True)
        self.progress.hide()
        self.status.showMessage("Hotovo" if ok else "Dokončené s chybami", 5000)
        self.worker = None