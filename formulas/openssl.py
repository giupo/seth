import os
import subprocess

from seth.formula import Formula


class OpenSSLFormula(Formula):
    name = "openssl"
    latest = "3.3.2"
    build_system = "custom"

    versions = {
        "3.3.2": {
            "url": "https://github.com/openssl/openssl/releases/download/openssl-3.3.2/openssl-3.3.2.tar.gz",
            "sha256": "2e8a40b01979afe8be0bbfb3de5dc1c6709fedb46d6c89f9e3a30f5d485afc8a",
        },
        "3.3.1": {
            "url": "https://github.com/openssl/openssl/releases/download/openssl-3.3.1/openssl-3.3.1.tar.gz",
            "sha256": "777cd596284c883375a2a7a11bf5d2786fc5413255efab20c50d6ffe6d020b7e",
        },
        "3.2.3": {
            "url": "https://github.com/openssl/openssl/releases/download/openssl-3.2.3/openssl-3.2.3.tar.gz",
            "sha256": "b7de5f5d09d4218e4f3a67e47d0ded0e32a48b86d26ca18f5ad694f1aa1e3ce0",
        },
    }

    def build(self, source_dir):
        nproc = os.cpu_count() or 1

        def run(cmd):
            print(f"  [run] {' '.join(str(c) for c in cmd)}")
            r = subprocess.run(cmd, cwd=source_dir)
            if r.returncode != 0:
                raise RuntimeError(f"Command failed: {' '.join(str(c) for c in cmd)}")

        run([
            "./Configure",
            f"--prefix={self.keg}",
            f"--openssldir={self.keg}/ssl",
            "linux-x86_64",
            "shared",
            "zlib",
        ])
        run(["make", f"-j{nproc}"])
        run(["make", "install_sw"])
