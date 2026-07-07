from seth.formula import Formula
from seth.types import BuildType

class PasswordStoreFormula(Formula):
    name = "password-store"
    latest = "1.7.4"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.MAKE

    versions = {
        "1.7.4": {
            "url": "https://git.zx2c4.com/password-store/snapshot/password-store-1.7.4.tar.xz",
            "sha256": "4c2d0a8b99df8915a87099607a8d912fd05d30651b6f014745c14e4ca8dbbfb7",
        },
    }

    # def configure_args(self) -> list[str]:
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    # def configure_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    def make_args(self) -> list[str]:
        """Variables/flags appended to every `make` invocation (e.g. CFLAGS=-O2)."""
        return [
            f"PREFIX={self.keg}",
        ] + self.extra_make_args

    # def cmake_args(self) -> list[str]:
    #     return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def build(self, source_dir:Path):
    #     pass

    # def post_install(self):
    #     pass

