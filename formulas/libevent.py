from seth.formula import Formula


class LibeventFormula(Formula):
    name = "libevent"
    latest = "2.1.12"
    dependencies = ["openssl"]

    versions = {
        "2.1.12": {
            "url": "https://github.com/libevent/libevent/releases/download/release-2.1.12-stable/libevent-2.1.12-stable.tar.gz",
            "sha256": "",  # sha256sum libevent-2.1.12-stable.tar.gz
        },
    }

    def configure_args(self):
        from seth.config import config
        openssl_ver = self.direct_deps.get("openssl", "")
        openssl_prefix = config.cellar / "openssl" / openssl_ver
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-static",
            f"--with-openssl={openssl_prefix}",
            "--disable-samples",
        ]
