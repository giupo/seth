from seth.formula import Formula
from seth.types import BuildType

class NinjaFormula(Formula):
    name = "ninja"
    latest = "1.13.2"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.CUSTOM

    versions = {
        "1.13.2": {
            "url": "https://github.com/ninja-build/ninja/releases/download/v1.13.2/ninja-linux.zip",
            "sha256": "",
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


    def build(self, source_dir):
        from pathlib import Path
        import shutil
        import stat

        Path(self.keg / "bin").mkdir(parents = True, exist_ok = True)
        src = source_dir / "ninja"
        dst = self.keg / "bin" / "ninja"
        shutil.copy2(src, dst)
        dst.chmod(
            dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )
