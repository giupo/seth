from seth.formula import Formula
from seth.types import BuildType

class Libgit2Formula(Formula):
    name = "libgit2"
    latest = "1.9.4"

    dependencies = ["openssl", "libssh2", "pcre2"]
    # build_dependencies = []
    build_system = BuildType.CMAKE

    versions = {
        "1.9.4": {
            "url": "https://github.com/libgit2/libgit2/archive/refs/tags/v1.9.4.tar.gz",
            "sha256": "824b73bd13647800fe4b566a1008ae77fea0e3e3424edab632fcfd8c0b14ba8b",
        }
    }

    # def configure_args(self) -> list[str]:
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    # def configure_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def make_args(self) -> list[str]:
    #     """Variables/flags appended to every `make` invocation (e.g. CFLAGS=-O2)."""
    #     return self.extra_make_args

    def cmake_args(self) -> list[str]:
        return [
            f"-DCMAKE_INSTALL_PREFIX={self.keg}",
            # "-DBUILD_EXAMPLES=ON",
            "-DUSE_SSH=ON",
            "-DUSE_HTTPS=ON",
            "-DUSE_GSSAPI=ON",
            "-DREGEX_BACKEND=pcre2",
        ] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def build(self, source_dir:Path):
    #     pass

    # def post_install(self):
    #     pass

