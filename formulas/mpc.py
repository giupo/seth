from seth.formula import Formula


class MpcFormula(Formula):
    name = "mpc"
    latest = "1.3.1"
    dependencies = ["gmp", "mpfr"]

    versions = {
        "1.3.1": {
            "url": "https://ftp.gnu.org/gnu/mpc/mpc-1.3.1.tar.gz",
            "sha256": "ab642492f5cf882b74aa0cb730cd410a81edcdbec895183ce930e706c1c759b8",
        },
        "1.2.1": {
            "url": "https://ftp.gnu.org/gnu/mpc/mpc-1.2.1.tar.gz",
            "sha256": "17503d2c395dfcf106b622dc142683c1199431d095367c6aacba6eec30340459",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-static",
            # gmp and mpfr found via LDFLAGS/CPPFLAGS from get_build_env()
        ]
