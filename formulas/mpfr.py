from seth.formula import Formula


class MpfrFormula(Formula):
    name = "mpfr"
    latest = "4.2.2"
    dependencies = ["gmp"]

    versions = {
        "4.2.2": {
            "url": "https://www.mpfr.org/mpfr-current/mpfr-4.2.2.tar.xz",
            "sha256": "b67ba0383ef7e8a8563734e2e889ef5ec3c3b898a01d00fa0a6869ad81c6ce01",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-static",
            # gmp found via LDFLAGS/CPPFLAGS from get_build_env()
        ]
