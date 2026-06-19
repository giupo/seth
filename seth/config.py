import configparser
import os
from pathlib import Path

_DEFAULT_ROOT = Path.home() / ".local" / "seth"
# When running from a .pyz this path resolves inside the zip (not a real dir).
_BUNDLED_FORMULAS = Path(__file__).parent.parent / "formulas"


class _Config:
    """Resolves seth's paths and settings from env vars, then the config file,
    then built-in defaults (in that precedence). Instantiated once as the
    module-level `config` singleton below.
    """

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

        # Search order: explicit override → remote cache → bundled (dev only).
        # If an explicit path is given, use only that.
        # _BUNDLED_FORMULAS is only added when it is a real directory on disk;
        # when running from a .pyz it resolves inside the zip and is_dir() → False.
        explicit = os.environ.get("SETH_FORMULAS") or cfg.get("paths", "formulas", fallback="")
        if explicit:
            self.formula_search_dirs = [Path(explicit)]
        else:
            self.formula_search_dirs = [self.remote_formulas_dir]
            if _BUNDLED_FORMULAS.is_dir():
                self.formula_search_dirs.append(_BUNDLED_FORMULAS)

        # Patches live inside each formula directory: <formula_dir>/patches/<pkg>/<file>.patch
        self.patch_dirs = [d / "patches" for d in self.formula_search_dirs]

        # Temp dir
        self.tmp_dir = os.environ.get(
            "TEMP", cfg.get(
                "paths", "tmp_dir", fallback=None
            )
        )
        
        
    def ensure_dirs(self):
        for d in (self.cellar, self.downloads, self.db_path.parent):
            d.mkdir(parents=True, exist_ok=True)
            

config = _Config()
