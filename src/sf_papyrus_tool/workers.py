from pathlib import Path
from PySide6.QtCore import QThread, Signal

from .tools import decompile, compile_psc
from .postprocess import process_file


class BaseWorker(QThread):
    log = Signal(str)
    finished = Signal(bool)


class DecompileWorker(BaseWorker):
    def __init__(self, champollion: str, files: list[Path], out_dir: Path, postprocess: bool):
        super().__init__()
        self.champollion = champollion
        self.files = files
        self.out_dir = out_dir
        self.postprocess_enabled = postprocess

    def run(self) -> None:
        success_count = 0
        self.log.emit(f"▶ Spúšťam hromadnú dekompiláciu ({len(self.files)} súborov)...")

        for pex in self.files:
            self.log.emit(f"\n--- {pex.name} ---")
            result = decompile(self.champollion, pex, self.out_dir)

            if result.stdout:
                self.log.emit(result.stdout)
            if result.stderr:
                self.log.emit(f"[stderr]\n{result.stderr}")

            if not result.ok:
                self.log.emit(f"✗ Champollion zlyhal (kód {result.returncode})")
                continue

            psc_path = self.out_dir / (pex.stem + ".psc")
            if not psc_path.exists():
                self.log.emit(f"✗ Očakávaný výstup sa nenašiel: {psc_path}")
                continue

            self.log.emit(f"✓ Vytvorené: {psc_path.name}")
            success_count += 1

            if self.postprocess_enabled:
                changes, warnings = process_file(psc_path)
                for w in warnings:
                    self.log.emit(f"  {w}")

        self.log.emit(f"\n✅ Hotovo. Úspešne dekompilovaných: {success_count} z {len(self.files)}")
        self.finished.emit(success_count > 0)


class CompileWorker(BaseWorker):
    def __init__(self, compiler: str, compiler_type: str, files: list[Path],
                 out_dir: Path, import_dir: str, game: str):
        super().__init__()
        self.compiler = compiler
        self.compiler_type = compiler_type
        self.files = files
        self.out_dir = out_dir
        self.import_dir = import_dir
        self.game = game

    def run(self) -> None:
        success_count = 0
        self.log.emit(f"▶ Spúšťam hromadnú kompiláciu ({len(self.files)} súborov)...")

        for psc in self.files:
            self.log.emit(f"\n--- {psc.name} ---")
            result = compile_psc(
                self.compiler, self.compiler_type, psc,
                self.out_dir, self.import_dir, self.game,
            )

            if result.stdout:
                self.log.emit(result.stdout)
            if result.stderr:
                self.log.emit(f"[stderr]\n{result.stderr}")

            if not result.ok:
                self.log.emit(f"✗ Kompilátor zlyhal (kód {result.returncode})")
                continue

            pex_path = self.out_dir / (psc.stem + ".pex")
            if pex_path.exists():
                self.log.emit(f"✓ Vytvorené: {pex_path.name} ({pex_path.stat().st_size} B)")
                success_count += 1
            else:
                self.log.emit(f"⚠ Kompilátor prešiel, ale {pex_path.name} sa nenašiel.")

        self.log.emit(f"\n✅ Hotovo. Úspešne skompilovaných: {success_count} z {len(self.files)}")
        self.finished.emit(success_count > 0)