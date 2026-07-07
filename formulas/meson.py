from seth.formula import Formula
from pathlib import Path

import stat

class MesonFormula(Formula):
    name = "meson"
    latest = "1.11.1"
    dependencies = ["python"]
    # build_dependencies = []
    build_system = "custom"
    
    versions = {
        "1.11.1": {
            "url": "https://github.com/mesonbuild/meson/releases/download/1.11.1/meson.pyz",
            "sha256": "",
        },
    }
        
    def build(self, source_dir: Path):
        # copy file and rename to meson
        Path(self.keg / "bin").mkdir(parents=True, exist_ok=True)        
        import shutil
        src = source_dir / "meson.pyz"
        dst = self.keg / "bin" / "meson"
        shutil.copy2(src, dst)
        dst.chmod(
            dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
