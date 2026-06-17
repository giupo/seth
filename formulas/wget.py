from seth.formula import Formula


class WgetFormula(Formula):
    name = "wget"
    version = "1.21.4"
    url = "https://ftp.gnu.org/gnu/wget/wget-1.21.4.tar.gz"
    sha256 = "81542f5cefb8faacc39bbbc6c82ded80e3e4a88505ae72ea51df27525bcde04c"
    dependencies = ["openssl"]

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            f"--with-ssl=openssl",
            f"--with-openssl",
        ]
