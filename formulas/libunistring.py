from seth.formula import Formula


class LibunistringFormula(Formula):
    name = "libunistring"
    latest = "1.4.2"

    versions = {
        "1.4.2": {
            "url": "https://ftp.gnu.org/gnu/libunistring/libunistring-1.4.2.tar.gz",
            "sha256": "e82664b170064e62331962126b259d452d53b227bb4a93ab20040d846fec01d8",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
        ]
