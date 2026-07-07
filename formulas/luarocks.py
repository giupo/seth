from seth.formula import Formula
from seth.types import BuildType

class LuarocksFormula(Formula):
    name = "luarocks"
    latest = "3.12.2"

    dependencies = ["lua<5.2"]
    # build_dependencies = []
    # build_system = BuildType.AUTOCONF

    versions = {
        "3.12.2": {
            "url": "https://luarocks.github.io/luarocks/releases/luarocks-3.12.2.tar.gz",
            "sha256": "b0e0c85205841ddd7be485f53d6125766d18a81d226588d2366931e9a1484492",
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

