from seth.formula import Formula
from seth.types import BuildType

class PandocFormula(Formula):
    name = "pandoc"
    latest = "3.10"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.CUSTOM

    versions = {
        "3.10": {
            "url": "https://github.com/jgm/pandoc/releases/download/3.10/pandoc-3.10-linux-amd64.tar.gz",
            "sha256": "e0f8af62d0f267d22baa5bcefe6d5dda3a097ccc60de794b759fe03159923244",
        },
    }

    # def configure_args(self) -> list[str]:
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    # def configure_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def make_args(self) -> list[str]:
    #     """Variables/flags appended to every `make` invocation (e.g. CFLAGS=-O2)."""
    #     return self.extra_make_args

    # def cmake_args(self) -> list[str]:
    #     return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    def build(self, source_dir):
        from pathlib import Path
        import shutil
        src = source_dir
        dst = self.keg
        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            target = dst / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)

    # def post_install(self):
    #     pass

