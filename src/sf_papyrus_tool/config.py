from dataclasses import dataclass
from PySide6.QtCore import QSettings


@dataclass
class ToolConfig:
    champollion: str = ""
    compiler: str = ""
    compiler_type: str = "caprica"   # "caprica" | "papyrus"
    import_dir: str = ""
    game: str = "starfield"
    postprocess: bool = True

    def load(self, qs: QSettings) -> None:
        self.champollion = qs.value("tools/champollion", "", str)
        self.compiler = qs.value("tools/compiler", "", str)
        self.compiler_type = qs.value("tools/compiler_type", "caprica", str)
        self.import_dir = qs.value("tools/import_dir", "", str)
        self.game = qs.value("tools/game", "starfield", str)
        self.postprocess = qs.value("tools/postprocess", True, bool)

    def save(self, qs: QSettings) -> None:
        qs.setValue("tools/champollion", self.champollion)
        qs.setValue("tools/compiler", self.compiler)
        qs.setValue("tools/compiler_type", self.compiler_type)
        qs.setValue("tools/import_dir", self.import_dir)
        qs.setValue("tools/game", self.game)
        qs.setValue("tools/postprocess", self.postprocess)
