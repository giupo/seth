from seth.formula import Formula


class GmpFormula(Formula):
    name = "gmp"
    latest = "6.3.0"

    versions = {
        "6.3.0": {
            "url": "https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz",
            "sha256": "a3c2b80201b89e68616f4ad30bc66aee4927c3ce50e33929ca819d5c43538898",
        },
        "6.2.1": {
            "url": "https://gmplib.org/download/gmp/gmp-6.2.1.tar.xz",
            "sha256": "fd4829912cddd12f84181c3451cc752be224643e87fac497b69edddadc49b4f2",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--enable-cxx",     # C++ support (needed by nettle)
        ]
