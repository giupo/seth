from seth.formula import Formula


class CurlFormula(Formula):
    name = "curl"
    latest = "8.10.1"
    dependencies = ["openssl", "zlib"]

    versions = {
        "8.10.1": {
            "url": "https://curl.se/download/curl-8.10.1.tar.gz",
            "sha256": "f76abb04f032aae80f49a3e4fd95e3c883a0dda4b4e6c51e4c85cfab8a95b80e",
        },
        "8.9.1": {
            "url": "https://curl.se/download/curl-8.9.1.tar.gz",
            "sha256": "291124a007ee5111997825940b3a2a2e479e864436a17d80b4dea3e4e1aa3ce3",
        },
        "8.7.1": {
            "url": "https://curl.se/download/curl-8.7.1.tar.gz",
            "sha256": "f91249c87f68ea00cf27c44fdfa5a78423e0b827d306bf89b1f68f7d8d4e9c10",
        },
    }

    def configure_args(self):
        from seth.config import config
        from seth import cellar as cel
        openssl_ver = cel.linked_version("openssl") or ""
        openssl_prefix = config.cellar / "openssl" / openssl_ver
        return [
            f"--prefix={self.keg}",
            f"--with-openssl={openssl_prefix}",
            "--with-zlib",
            "--enable-versioned-symbols",
        ]
