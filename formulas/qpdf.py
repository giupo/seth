from seth.formula import Formula
from seth.types import BuildType
from seth.config import config

class QpdfFormula(Formula):
    name = "qpdf"
    latest = "12.3.2"

    # dependencies = []
    build_dependencies = ["gcc"]
    build_system = BuildType.CMAKE

    versions = {
        "12.3.2": {
            "url": "https://github.com/qpdf/qpdf/releases/download/v12.3.2/qpdf-12.3.2.tar.gz",
            "sha256": "6cba2f9f2cd887d905faeb99e0e51a307b217920d1bbf3e9cfbb2e8178a2deda",
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

    def cmake_args(self) -> list[str]:
        gcc_ver = self.direct_deps.get("gcc")
        gcc_bin = (config.cellar / "gcc" / gcc_ver / "bin") if gcc_ver else (config.root / "bin")
        return [
            f"-DCMAKE_INSTALL_PREFIX={self.keg}",
            f"-DCMAKE_C_COMPILER={gcc_bin}/gcc",
            f"-DCMAKE_CXX_COMPILER={gcc_bin}/g++",
            "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
        ] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def build(self, source_dir:Path):
    #     pass

    # def post_install(self):
    #     pass

