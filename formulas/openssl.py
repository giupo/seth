from seth.formula import Formula


class OpenSSLFormula(Formula):
    name = "openssl"
    version = "3.3.2"
    url = "https://github.com/openssl/openssl/releases/download/openssl-3.3.2/openssl-3.3.2.tar.gz"
    sha256 = "2e8a40b01979afe8be0bbfb3de5dc1c6709fedb46d6c89f9e3a30f5d485afc8a"
    build_system = "custom"

    def build(self, source_dir):
        import subprocess
        from pathlib import Path

        def run(cmd):
            import os
            print(f"  [run] {' '.join(str(c) for c in cmd)}")
            r = subprocess.run(cmd, cwd=source_dir)
            if r.returncode != 0:
                raise RuntimeError(f"Command failed: {' '.join(str(c) for c in cmd)}")

        run(["./Configure", f"--prefix={self.keg}", "--openssldir={}/ssl".format(self.keg), "linux-x86_64", "shared", "zlib"])
        run(["make", f"-j{__import__('os').cpu_count() or 1}"])
        run(["make", "install_sw"])
