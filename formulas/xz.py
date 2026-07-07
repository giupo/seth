from seth.formula import Formula


class XzFormula(Formula):
    name = "xz"
    latest = "5.8.3"
    # dependencies = []
    # build_dependencies = []

    versions = {
        "5.8.3": {
            "url": "https://github.com/tukaani-project/xz/releases/download/v5.8.3/xz-5.8.3.tar.gz",
            "sha256": "3d3a1b973af218114f4f889bbaa2f4c037deaae0c8e815eec381c3d546b974a0",
        },
    }

    # def configure_args(self):
    #     return [
    #         f"--prefix={self.keg}",
    #         "--enable-shared",
    #     ]
