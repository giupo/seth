from seth.formula import Formula
from seth.types import BuildType

class GitFormula(Formula):
    name = "git"
    latest = "2.54.0"

    # dependencies = []
    # build_dependencies = []
    # build_system = BuildType.AUTOCONF

    versions = {
        "2.54.0": {
            "url": "https://www.kernel.org/pub/software/scm/git/git-2.54.0.tar.gz",
            "sha256": "45e8107643a44e3ce46f5665beb35af3932fb0d70017687905ab5d4e3aafa8eb",
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    def configure_args(self) -> list[str]:
        return [f"--prefix={self.keg}"] + self.extra_configure_args

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

