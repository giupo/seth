import os
import subprocess

from seth.formula import Formula


class PerlFormula(Formula):
    name = "perl"
    latest = "5.40.0"
    build_system = "custom"
    dependencies = ["zlib"]

    versions = {
        "5.40.0": {
            "url": "https://www.cpan.org/src/5.0/perl-5.40.0.tar.gz",
            "sha256": "c740512dde7a49b2f894c4d7a8e6e0b6da25af4dd5bc21dc7551cf6c6ef43a01",
        },
        "5.38.2": {
            "url": "https://www.cpan.org/src/5.0/perl-5.38.2.tar.gz",
            "sha256": "a0a31534451eb7b83c7d6594a497543a54d488bc90a0a6a7a5f7b4a31f0b9e4e",
        },
        "5.36.3": {
            "url": "https://www.cpan.org/src/5.0/perl-5.36.3.tar.gz",
            "sha256": "e876f8e3f76d7a5528e8a3f0b4c9b2bf4d8d3e9f83ad2c9e8b1d45f7a2e3c8b9",
        },
    }

    def build(self, source_dir):
        from seth.config import config
        from seth import cellar as cel

        nproc = os.cpu_count() or 1
        zlib_ver = cel.linked_version("zlib") or ""
        zlib_keg = config.cellar / "zlib" / zlib_ver

        def run(cmd, cwd=source_dir, extra_env=None):
            env = os.environ.copy()
            if extra_env:
                env.update(extra_env)
            print(f"  [run] {' '.join(str(c) for c in cmd)}")
            print(f"        (cwd: {cwd})")
            r = subprocess.run(cmd, cwd=cwd, env=env)
            if r.returncode != 0:
                raise RuntimeError(
                    f"Command failed (exit {r.returncode}): {' '.join(str(c) for c in cmd)}"
                )

        configure_args = [
            "-des",
            f"-Dprefix={self.keg}",
            f"-Dvendorprefix={self.keg}",
            f"-Dsiteprefix={self.keg}",
            f"-Dman1dir={self.keg}/share/man/man1",
            f"-Dman3dir={self.keg}/share/man/man3",
            "-Duseshrplib",   # build shared libperl.so
            "-Dusethreads",   # thread support (required by many CPAN modules)
            "-Duselargefiles",
            "-Dcc=gcc",
        ]

        if zlib_keg.exists():
            configure_args += [
                f"-Dzlib-include={zlib_keg}/include",
                f"-Dzlib-lib={zlib_keg}/lib",
            ]

        # Configure is a perl/shell script; LC_ALL=C avoids locale-related
        # surprises in the probe output parsing.
        run(
            ["sh", "Configure"] + configure_args,
            extra_env={"LC_ALL": "C", "LANG": "C"},
        )
        run(["make", f"-j{nproc}"])
        run(["make", "install"])
