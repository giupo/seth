from seth.formula import Formula


class CurlFormula(Formula):
    name = "curl"
    latest = "8.20.0"
    dependencies = ["openssl>=3.0", "zlib>=1.2", "perl"]
    build_dependencies = ["pkgconfig"]

    versions = {
        "8.20.0": {
            "url": "https://curl.se/download/curl-8.20.0.tar.gz",
            "sha256": "fc5819cad3f9f5482669adcdc49a782c15f36d2a0715b395b06d9173593d2dc0"
        },
        "8.10.1": {
            "url": "https://curl.se/download/curl-8.10.1.tar.gz",
            "sha256": "d15ebab765d793e2e96db090f0e172d127859d78ca6f6391d7eafecfd894bbc0",
        },
    }

    def configure_args(self):
        from seth.config import config
        openssl_ver = self.direct_deps.get("openssl", "")
        openssl_prefix = config.cellar / "openssl" / openssl_ver
        return [
            f"--prefix={self.keg}",
            f"--with-openssl={openssl_prefix}",
            "--with-zlib",
            "--enable-versioned-symbols",
        ]
