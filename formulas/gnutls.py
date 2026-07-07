from seth.formula import Formula


class GnutlsFormula(Formula):
    name = "gnutls"
    latest = "3.8.8"
    dependencies = ["nettle>=3.9", "libtasn1>=4.19", "brotli"]

    versions = {
        "3.8.8": {
            "url": "https://www.gnupg.org/ftp/gcrypt/gnutls/v3.8/gnutls-3.8.8.tar.xz",
            "sha256": "ac4f020e583880b51380ed226e59033244bc536cad2623f2e26f5afa2939d8fb",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--without-p11-kit",        # skip PKCS#11 (pulls in p11-kit dep)
            "--without-idn",            # skip IDN (pulls in libidn2/libunistring)
            "--disable-libdane",        # skip DANE (needs unbound)
            "--disable-doc",
            "--disable-tools",          # skip CLI tools (gnutls-cli etc.)
            "--disable-tests",
            "--with-included-unistring"
            # nettle, libtasn1, gmp found via PKG_CONFIG_PATH + LDFLAGS from get_build_env()
        ]
