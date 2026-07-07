from seth.formula import Formula
from seth.types import BuildType

class Pcre2Formula(Formula):
    name = "pcre2"
    latest = "10.47"

    dependencies = ["readline", "perl"]
    # build_dependencies = []
    build_system = BuildType.AUTOCONF

    versions = {
        "10.47": {
            "url": "https://github.com/PCRE2Project/pcre2/releases/download/pcre2-10.47/pcre2-10.47.tar.gz",
            "sha256": "c08ae2388ef333e8403e670ad70c0a11f1eed021fd88308d7e02f596fcd9dc16",
        },
    }

    def configure_args(self):
         return [
             f"--prefix={self.keg}",
             "--enable-pcre2-16",
             "--enable-pcre2-32",
             "--enable-jit=auto",
             "--enable-pcre2grep-libz",
             "--enable-pcre2grep-libbz2",
             # "--enable-pcre2test-libedit",
             "--with-link-size=4",
             "--enable-newline-is-any",
             "--with-pcre2grep-bufsize=51200",
             "--with-pcre2grep-max-bufsize=2097152"
         ]
