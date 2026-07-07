from seth.formula import Formula
from seth.types import BuildType

class CmakeFormula(Formula):
    name = "cmake"
    latest = "4.3.4"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.CUSTOM

    versions = {
        "4.3.4": {
            "url": "https://github.com/Kitware/CMake/releases/download/v4.3.4/cmake-4.3.4-linux-x86_64.tar.gz",
            "sha256": "ca6f08ccbd5e6b0a9068d33317d0d1aff7278d08cccaed4529b8fbead7942a68",
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
        dest_dir = Path(self.keg)
        dest_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():
            target = dest_dir / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)
