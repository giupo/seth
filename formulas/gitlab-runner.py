from seth.formula import Formula
from seth.types import BuildType

class GitlabRunnerFormula(Formula):
    name = "gitlab-runner"
    latest = "latest"

    # dependencies = []
    # build_dependencies = []
    build_system = BuildType.CUSTOM

    versions = {
        "latest": {
            "url": "https://s3.dualstack.us-east-1.amazonaws.com/gitlab-runner-downloads/latest/binaries/gitlab-runner-linux-amd64",
            "sha256": "8c8ea572b9f0d40e93b876b90c7d093eb403a41bbadbbf9a0fcf27b6b75c2800",
        },
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

    # def cmake_args(self) -> list[str]:
    #     return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #     return [f"--prefix={self.keg}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    def build(self, source_dir):
        import shutil
        import stat
        from pathlib import Path

        Path(self.keg / "bin").mkdir(parents=True, exist_ok=True)
        src = source_dir / "gitlab-runner-linux-amd64"
        dst = self.keg / "bin" / "gitlab-runner"
        shutil.copy2(src, dst)
        dst.chmod(
            dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

    # def post_install(self):
    #     pass

