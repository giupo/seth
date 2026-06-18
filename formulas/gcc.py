import os
import subprocess

from seth import colors as col
from seth.formula import Formula


class GccFormula(Formula):
    name = "gcc"
    latest = "16.1.0"
    build_system = "custom"
    dependencies = ["gmp", "mpfr", "mpc", "zlib"]

    versions = {
        "16.1.0": {
            "url": "https://ftp.gnu.org/gnu/gcc/gcc-16.1.0/gcc-16.1.0.tar.xz",
            "sha256": "50efb4d94c3397aff3b0d61a5abd748b4dd31d9d3f2ab7be05b171d36a510f79",
        },
    }

    def build(self, source_dir):
        from seth.builder import get_build_env
        from seth.config import config
        from seth import cellar as cel

        env = get_build_env()
        nproc = os.cpu_count() or 1

        def keg_of(name):
            ver = cel.linked_version(name) or ""
            return config.cellar / name / ver

        # GCC must be configured and built outside the source tree.
        build_dir = source_dir / "_build"
        build_dir.mkdir(exist_ok=True)

        configure_args = [
            f"--prefix={self.keg}",
            # Build C, C++ and the JIT library (libgccjit).
            # --enable-host-shared is REQUIRED: it makes the compiler
            # itself position-independent, which is a prerequisite for
            # building libgccjit as a shared library.
            "--enable-languages=c,c++,jit",
            "--enable-host-shared",
            "--disable-multilib",       # 64-bit only, no 32-bit compat
            "--disable-bootstrap",      # single-stage build (uses system gcc)
            "--disable-nls",            # no i18n (smaller, faster)
            "--with-system-zlib",
            f"--with-gmp={keg_of('gmp')}",
            f"--with-mpfr={keg_of('mpfr')}",
            f"--with-mpc={keg_of('mpc')}",
        ]

        def run(cmd, cwd=build_dir):
            cmd_str = " ".join(str(c) for c in cmd)
            print(f"  {col.tag('run')}{col.dim(cmd_str)}")
            print(f"  {' ' * 11}{col.dim(f'(cwd: {cwd})')}")
            r = subprocess.run(cmd, cwd=cwd, env=env)
            if r.returncode != 0:
                raise RuntimeError(
                    f"Command failed (exit {r.returncode}): {cmd_str}"
                )

        run([str(source_dir / "configure")] + configure_args)
        run(["make", f"-j{nproc}"])
        run(["make", "install"])
