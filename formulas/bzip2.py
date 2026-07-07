from seth.formula import Formula


class Bzip2Formula(Formula):
    name = "bzip2"
    latest = "1.0.8"
    # dependencies = []
    # build_dependencies = []
    build_system = "make"
    versions = {
        "1.0.8": {
            "url": "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz",
            "sha256": "ab5a03176ee106d3f0fa90e381da478ddae405918153cca248e682cd0c4a2269",
        },
    }

    def make_args(self):
        return [
            f"PREFIX={self.keg}"
        ]
