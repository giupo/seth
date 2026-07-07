from seth.formula import Formula
from seth.types import BuildType

class NeovimFormula(Formula):
    name = "neovim"
    latest = "0.12.3"

    dependencies = ["luarocks", "lazygit", "fzf"]
    # build_dependencies = []
    build_system = BuildType.MAKE

    versions = {
        "0.12.3": {
            "url": "https://github.com/neovim/neovim/archive/refs/tags/v0.12.3.tar.gz",
            "sha256": "36a6c66bfbba5d96fa512110aecddb981148a4d013b5ecd01a42877c49855a41",
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    # def configure_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    def make_args(self) -> list[str]:
        """Variables/flags appended to every `make` invocation (e.g. CFLAGS=-O2)."""
        return [
	    f"CMAKE_INSTALL_PREFIX={self.keg}",
            "CMAKE_BUILD_TYPE=Release",
	] + self.extra_make_args

    # def cmake_args(self) -> list[str]:
    #    return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def post_install(self):
    #     pass

