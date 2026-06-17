from seth.formula import Formula


class CurlFormula(Formula):
    name = "curl"
    version = "8.10.1"
    url = "https://curl.se/download/curl-8.10.1.tar.gz"
    sha256 = "73a4b0e2a4a402e4b40cf4a8a8a7b3a229e4ebbbf6e35b26e2c1c7d5a2a2a3b3"
    dependencies = ["openssl", "zlib"]

    def configure_args(self):
        from seth.config import config
        from seth import cellar as cel
        openssl_ver = cel.installed_version("openssl") or ""
        openssl_prefix = config.cellar / "openssl" / openssl_ver
        return [
            f"--prefix={self.keg}",
            f"--with-openssl={openssl_prefix}",
            "--with-zlib",
            "--enable-versioned-symbols",
        ]
