from seth.formula import Formula


class Libssh2Formula(Formula):
    name = "libssh2"
    latest = "1.11.1"
    dependencies = ["openssl", "zlib"]
    build_system = "cmake"

    versions = {
        "1.11.1": {
            "url": "https://libssh2.org/download/libssh2-1.11.1.tar.gz",
            "sha256": "",  # sha256sum libssh2-1.11.1.tar.gz
        },
        "1.11.0": {
            "url": "https://libssh2.org/download/libssh2-1.11.0.tar.gz",
            "sha256": "",
        },
    }

    def cmake_args(self):
        from seth.config import config
        from seth import cellar
        openssl_ver = cellar.linked_version("openssl") or ""
        openssl_root = config.cellar / "openssl" / openssl_ver
        return [
            f"-DCMAKE_INSTALL_PREFIX={self.keg}",
            "-DBUILD_SHARED_LIBS=ON",
            "-DCRYPTO_BACKEND=OpenSSL",
            f"-DOPENSSL_ROOT_DIR={openssl_root}",
            "-DCMAKE_BUILD_TYPE=Release",
        ]
