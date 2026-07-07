from seth.formula import Formula
from seth.types import BuildType

class LibffiFormula(Formula):
    name = "libffi"
    latest = "3.5.2"

    dependencies = ["texinfo"]
    # build_dependencies = []
    build_system = BuildType.AUTOGEN
    
    versions = {
        "3.5.2": {
            "url": "https://github.com/libffi/libffi/archive/refs/tags/v3.5.2.tar.gz",
            "sha256": "dd19253d3007f366319a51d248a40c9e5fcace4498cbea990b566291844e4e30",
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
            "MAKEINFO=true", # don't bother me with makeinfo, please
        ]

    # def cmake_args(self) -> list[str]:
    #    return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def post_install(self):
    #     pass

