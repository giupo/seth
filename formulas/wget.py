from seth.formula import Formula


class WgetFormula(Formula):
    name = "wget"
    latest = "1.21.4"
    dependencies = ["openssl"]

    versions = {
        "1.21.4": {
            "url": "https://ftp.gnu.org/gnu/wget/wget-1.21.4.tar.gz",
            "sha256": "81542f5cefb8faacc39bbbc6c82ded80e3e4a88505ae72ea51df27525bcde04c",
        },
        "1.21.3": {
            "url": "https://ftp.gnu.org/gnu/wget/wget-1.21.3.tar.gz",
            "sha256": "e1b2a57c718f37a7e8e6a91e1f11eed68a0b0f7e10bd65a1b0946f0e1f7b9be9",
        },
        "1.21.2": {
            "url": "https://ftp.gnu.org/gnu/wget/wget-1.21.2.tar.gz",
            "sha256": "f7dca2e4a3e94e23f5df0f3e30e28bf25f4dd3ec5cb2d3def3c8e1fad5f59abb",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--with-ssl=openssl",
            "--with-openssl",
        ]
