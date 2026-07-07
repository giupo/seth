from seth.formula import Formula
from seth.types import BuildType
from pathlib import Path

import stat

class LazygitFormula(Formula):
    name = "lazygit"
    latest = "0.62.2"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.CUSTOM

    versions = {
        "0.62.2": {
            "url": "https://github.com/jesseduffield/lazygit/releases/download/v0.62.2/lazygit_0.62.2_linux_x86_64.tar.gz",
            "sha256": "8b9a4c2d0969cbea92b45c956dd2a44e1ba76900c9df49f1c60984045ce77984"
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    # def configure_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def make_args(self) -> list[str]:
    #    """Variables/flags appended to every `make` invocation (e.g. CFLAGS=-O2)."""
    #     return self.extra_make_args

    # def cmake_args(self) -> list[str]:
    #    return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def post_install(self):
    #     pass

    def build(self, source_dir: Path):
        src = source_dir / "lazygit"
        dst = Path(self.keg) / "bin"
        dst.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(src, dst)
        dst.chmod(
            dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
