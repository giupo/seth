from seth.formula import Formula
from seth.types import BuildType

class RFormula(Formula):
    name = "R"
    latest = "4.6.1"

    # dependencies = []
    # build_dependencies = []
    # build_system = BuildType.AUTOCONF

    versions = {
        "4.6.1": {
            "url": "https://cran.r-project.org/src/base/R-4/R-4.6.1.tar.gz",
            "sha256": "4da6e61d2c0aac5f14a2e7e432cb5fcc269efe83da4293050ba7f03dff4e2cf4",
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    def configure_args(self) -> list[str]:
        return [
            f"--prefix={self.keg}",
            "--enable-R-shlib",
            "--enable-R-profiling",
            "--enable-memory-profiling",
            "--enable-BLAS-shlib",
            "--enable-prebuilt-html",
            "--with-readline",
            "--with-tcltk",
            "--with-blas",
            "--with-lapack"
        ] + self.extra_configure_args

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

