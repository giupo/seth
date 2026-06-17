from seth.formula import Formula


class ZlibFormula(Formula):
    name = "zlib"
    latest = "1.3.2"

    versions = {
        "1.3.2": {
            "url": "https://zlib.net/zlib-1.3.2.tar.gz",
            "sha256": "bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16",
        },
    }
