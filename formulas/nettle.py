from seth.formula import Formula


class NettleFormula(Formula):
    name = "nettle"
    latest = "3.9.1"
    dependencies = ["gmp"]

    versions = {
        "3.9.1": {
            "url": "https://ftp.gnu.org/gnu/nettle/nettle-3.9.1.tar.gz",
            "sha256": "ccfeff981b0ca71bbd6fbcb054f407c60ffb644389a5be80d6716d5b550c6ce3",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-documentation",
        ]
        # gmp is found automatically via LDFLAGS/CPPFLAGS set by get_build_env()
