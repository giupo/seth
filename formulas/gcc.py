import os
import subprocess

from seth.formula import Formula


class GccFormula(Formula):
    name = "gcc"
    latest = "14.2.0"
    build_system = "custom"
    dependencies = ["gmp", "mpfr", "mpc", "zlib"]

    versions = {
        "14.2.0": {
            "url": "https://ftp.gnu.org/gnu/gcc/gcc-14.2.0/gcc-14.2.0.tar.xz",
            "sha256": "a7b39bc69cbf9e25826c5a60ab26477001f7c08d85cec04bc0e29cabed6f3cc9",
        },
        "13.3.0": {
            "url": "https://ftp.gnu.org/gnu/gcc/gcc-13.3.0/gcc-13.3.0.tar.xz",
            "sha256": "0845e9621c9543a13f484e94584a49ffc0129970e9914624235fc1d061a0c083",
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
            print(f"  [run] {' '.join(str(c) for c in cmd)}")
            print(f"        (cwd: {cwd})")
            r = subprocess.run(cmd, cwd=cwd, env=env)
            if r.returncode != 0:
                raise RuntimeError(
                    f"Command failed (exit {r.returncode}): {' '.join(str(c) for c in cmd)}"
                )

        run([str(source_dir / "configure")] + configure_args)
        run(["make", f"-j{nproc}"])
        run(["make", "install"])
