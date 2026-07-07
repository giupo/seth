from seth.formula import Formula


class GettextFormula(Formula):
    name = "gettext"
    latest = "1.0.0"
    # dependencies = []
    # build_dependencies = []

    versions = {
        "1.0.0": {
            "url": "https://ftp.gnu.org/gnu/gettext/gettext-1.0.tar.gz",
            "sha256": "85d99b79c981a404874c02e0342176cf75c7698e2b51fe41031cf6526d974f1a"
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]
