from seth.formula import Formula
from seth.types import BuildType


from pathlib import Path
import stat


class FzfFormula(Formula):
    name = "fzf"
    latest = "0.73.1"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.CUSTOM

    versions = {
        "0.73.1": {
            "url": "https://github.com/junegunn/fzf/releases/download/v0.73.1/fzf-0.73.1-linux_amd64.tar.gz",
            "sha256": "f3252c2c366bc1700d3c85781ec8c9695998927ac127870eb049ceea2d540f8a",
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
        exec = "fzf"
        src = source_dir / exec
        Path(self.keg, "bin").mkdir(parents=True, exist_ok=True)
        dst = self.keg / "bin" / exec
        import shutil
        shutil.copy2(src, dst)
        dst.chmod(
            dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )


