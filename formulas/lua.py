from seth.formula import Formula
from seth.types import BuildType

class LuaFormula(Formula):
    name = "lua"
    latest = "5.4.8"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.MAKE

    versions = {
        "5.4.8": {
            "url": "https://www.lua.org/ftp/lua-5.4.8.tar.gz",
            "sha256": "4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae",
        },
        "5.1.5": {
            "url": "https://www.lua.org/ftp/lua-5.1.5.tar.gz",
            "sha256": "2640fc56a795f29d28ef15e13c34a47e223960b0240e8cb0a82d9b0738695333"
        }
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
            "linux",
            f"INSTALL_TOP={self.keg}",
        ] + self.extra_make_args

    # def cmake_args(self) -> list[str]:
    #    return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def post_install(self):
    #     pass

