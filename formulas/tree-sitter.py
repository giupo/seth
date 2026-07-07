from seth.formula import Formula
from seth.types import BuildType

class TreeSitterFormula(Formula):
    name = "tree-sitter"
    latest = "0.26.9"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.MAKE

    versions = {
        "0.26.9": {
            "url": "https://github.com/tree-sitter/tree-sitter/archive/refs/tags/v0.26.9.tar.gz",
            "sha256": "8e14780500933f43d86662fcaa1b0ce99ebe9c220f4680bc929dce09a0e0cfc6",
        },
        "0.25.10": {
            "url": "https://github.com/tree-sitter/tree-sitter/archive/refs/tags/v0.25.10.tar.gz",
            "sha256": "ad5040537537012b16ef6e1210a572b927c7cdc2b99d1ee88d44a7dcdc3ff44c",
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
        return [
            f"PREFIX={self.keg}",
        ]

    # def cmake_args(self) -> list[str]:
    #    return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #    return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def post_install(self):
    #     pass

