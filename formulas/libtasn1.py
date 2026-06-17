from seth.formula import Formula


class Libtasn1Formula(Formula):
    name = "libtasn1"
    latest = "4.19.0"

    versions = {
        "4.19.0": {
            "url": "https://ftp.gnu.org/gnu/libtasn1/libtasn1-4.19.0.tar.gz",
            "sha256": "1613f0ac1cf484d6e4cf8b9b34d5f0c2e72b3b654ebeb0d32b01d08f68a6f9e8",
        },
        "4.18.0": {
            "url": "https://ftp.gnu.org/gnu/libtasn1/libtasn1-4.18.0.tar.gz",
            "sha256": "9af850bc4d25dc40b90bc14012a35c04d32c6a95c88a7b5ccd558e7c8fd99aa8",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-doc",    # skip gtk-doc dependency
        ]
