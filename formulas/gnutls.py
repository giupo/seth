from seth.formula import Formula


class GnutlsFormula(Formula):
    name = "gnutls"
    latest = "3.8.8"
    dependencies = ["nettle>=3.9", "libtasn1>=4.19"]

    versions = {
        "3.8.8": {
            "url": "https://www.gnupg.org/ftp/gcrypt/gnutls/v3.8/gnutls-3.8.8.tar.xz",
            "sha256": "13b4be42e79a3e25da6adcac0d2bff0e6cd36f1c67f6ef53bcf3d3e5efcff78e",
        },
        "3.8.4": {
            "url": "https://www.gnupg.org/ftp/gcrypt/gnutls/v3.8/gnutls-3.8.4.tar.xz",
            "sha256": "3b6588a98a0e6a75d58c51fb07fc4a9d7d42ee4c15791f9b6e34e48cbc1ec070",
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
            # nettle, libtasn1, gmp found via PKG_CONFIG_PATH + LDFLAGS from get_build_env()
        ]
