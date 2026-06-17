import configparser
import os
from pathlib import Path

_DEFAULT_ROOT = Path.home() / ".local" / "seth"
_BUNDLED_FORMULAS = Path(__file__).parent.parent / "formulas"


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
        self.downloads = self.root / "Downloads"
        self.db_path = self.root / "var" / "seth" / "db.json"
        self.remote_formulas_dir = self.root / "var" / "seth" / "formulas"

        # URL of the remote formula repository (git or tar.gz)
        self.formulas_url = os.environ.get(
            "SETH_FORMULAS_URL",
            cfg.get("formulas", "url", fallback=""),
        )

        # Search order: explicit override → remote cache → bundled.
        # If an explicit path is given, use only that.
        explicit = os.environ.get("SETH_FORMULAS") or cfg.get("paths", "formulas", fallback="")
        if explicit:
            self.formula_search_dirs = [Path(explicit)]
        else:
            self.formula_search_dirs = [self.remote_formulas_dir, _BUNDLED_FORMULAS]

    def ensure_dirs(self):
        for d in (self.cellar, self.downloads, self.db_path.parent):
            d.mkdir(parents=True, exist_ok=True)


config = _Config()
