from seth.formula import Formula


class NettleFormula(Formula):
    name = "nettle"
    latest = "3.9.1"
    dependencies = ["gmp"]

    versions = {
        "3.9.1": {
            "url": "https://ftp.gnu.org/gnu/nettle/nettle-3.9.1.tar.gz",
            "sha256": "ccfeff981b0ca71bbd6fbcb054f407c60ffb644e6f9a9e22a8c5ac89cf9cc44f",
        },
        "3.9": {
            "url": "https://ftp.gnu.org/gnu/nettle/nettle-3.9.tar.gz",
            "sha256": "2a2ef80a84a28d4f055e6d27dc77bd5609f89a0f02f42625f1d50e42f8d26e80",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-documentation",
        ]
        # gmp is found automatically via LDFLAGS/CPPFLAGS set by get_build_env()
