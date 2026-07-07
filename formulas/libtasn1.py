from seth.formula import Formula


class Libtasn1Formula(Formula):
    name = "libtasn1"
    latest = "4.19.0"

    versions = {
        "4.19.0": {
            "url": "https://ftp.gnu.org/gnu/libtasn1/libtasn1-4.19.0.tar.gz",
            "sha256": "1613f0ac1cf484d6ec0ce3b8c06d56263cc7242f1c23b30d82d23de345a63f7a",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-doc",    # skip gtk-doc dependency
        ]
