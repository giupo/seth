from seth.formula import Formula
from seth.types import BuildType

class ReadlineFormula(Formula):
    name = "readline"
    latest = "8.3"

    dependencies = ["ncurses"]
    # build_dependencies = []
    # build_system = BuildType.AUTOCONF

    versions = {
        "8.3": {
            "url": "https://ftp.gnu.org/gnu/readline/readline-8.3.tar.gz",
            "sha256": "fe5383204467828cd495ee8d1d3c037a7eba1389c22bc6a041f627976f9061cc",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--with-curses",
            "--with-shared-termcap-library",
        ]

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

