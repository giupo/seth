from seth.formula import Formula
from seth.types import BuildType

class TexinfoFormula(Formula):
    name = "texinfo"
    latest = "7.3"

    # dependencies = []
    # build_dependencies = []
    # build_system = BuildType.AUTOCONF
    
    versions = {
        "7.3": {
            "url": "https://ftp.gnu.org/gnu/texinfo/texinfo-7.3.tar.gz",
            "sha256": "4fc30d71e00416f0b4884994f1db9db2901f03603f8e69d92dd46fa018d998d7",
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

