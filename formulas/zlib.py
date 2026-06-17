from seth.formula import Formula


class ZlibFormula(Formula):
    name = "zlib"
    latest = "1.3.1"

    versions = {
        "1.3.1": {
            "url": "https://zlib.net/zlib-1.3.1.tar.gz",
            "sha256": "9a93b2b7dfdac77ceba5a558a580e74667dd6fede4585b91eefb60f03b72df23",
        },
        "1.3": {
            "url": "https://zlib.net/fossils/zlib-1.3.tar.gz",
            "sha256": "ff0ba4c292013dbc27530b3a81e1f9a813cd39de01ca5e0f8bf355702efa593e",
        },
        "1.2.13": {
            "url": "https://zlib.net/fossils/zlib-1.2.13.tar.gz",
            "sha256": "b3a24de97a8fdbc835b9833169501030b8977031bcb54b3b3ac13740f846ab30",
        },
    }
