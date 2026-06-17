from seth.formula import Formula


class MpfrFormula(Formula):
    name = "mpfr"
    latest = "4.2.1"
    dependencies = ["gmp"]

    versions = {
        "4.2.1": {
            "url": "https://www.mpfr.org/mpfr-current/mpfr-4.2.1.tar.xz",
            "sha256": "277807353a6726978996945af13e52829e3abd7a9a5b7fb2793894e18f1fcbb2",
        },
        "4.2.0": {
            "url": "https://www.mpfr.org/mpfr-4.2.0/mpfr-4.2.0.tar.xz",
            "sha256": "06a378df13501248c1b2db5aa977a2c8126ae849a9d9b7be2546fb4a9c26d993",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-static",
            # gmp found via LDFLAGS/CPPFLAGS from get_build_env()
        ]
