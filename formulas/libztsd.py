from seth.formula import Formula


class LibztsdFormula(Formula):
    name = "libztsd"
    latest = "1.5.7"
    # dependencies = []
    # build_dependencies = []
    build_system = "make"
    versions = {
        "1.5.7": {
            "url": "https://github.com/pexip/os-libzstd/archive/refs/tags/upstream/1.5.7+dfsg.tar.gz",
            "sha256": "",
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]

    def make_args(self):
        return [
            f"PREFIX={self.keg}"
        ]
