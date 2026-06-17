import configparser
import os
from pathlib import Path

_DEFAULT_ROOT = Path.home() / ".local" / "seth"


class _Config:
    def __init__(self):
        cfg = configparser.ConfigParser()
        config_file = Path(
            os.environ.get(
                "SETH_CONFIG",
                Path.home() / ".config" / "seth" / "seth.conf",
            )
        )
        cfg.read(config_file)

        self.root = Path(
            os.environ.get("SETH_ROOT", cfg.get("paths", "root", fallback=str(_DEFAULT_ROOT)))
        )
        self.cellar = Path(
            os.environ.get(
                "SETH_CELLAR",
                cfg.get("paths", "cellar", fallback=str(self.root / "Cellar")),
            )
        )
        self.formulas_dir = Path(
            os.environ.get(
                "SETH_FORMULAS",
                cfg.get(
                    "paths",
                    "formulas",
                    fallback=str(Path(__file__).parent.parent / "formulas"),
                ),
            )
        )
        self.downloads = self.root / "Downloads"
        self.db_path = self.root / "var" / "seth" / "db.json"

    def ensure_dirs(self):
        for d in (self.cellar, self.downloads, self.db_path.parent):
            d.mkdir(parents=True, exist_ok=True)


config = _Config()
