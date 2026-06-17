from seth.formula import Formula


class EmacsFormula(Formula):
    name = "emacs"
    latest = "30.2"
    dependencies = ["ncurses", "libxml2", "gnutls", "zlib", "gcc"]
    build_dependencies = ["pkgconfig"]

    versions = {
        "30.2": {
            "url": "https://ftp.gnu.org/gnu/emacs/emacs-30.2.tar.gz",
            "sha256": "1d79a4ba4d6596f302a7146843fe59cf5caec798190bcc07c907e7ba244b076d",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--without-x",              # terminal only, no X11
            "--without-ns",             # no macOS Cocoa
            "--without-gconf",
            "--without-gsettings",
            "--without-dbus",
            "--without-selinux",
            "--without-imagemagick",
            "--with-gnutls",            # TLS for package.el / url.el
            "--with-xml2",              # libxml2
            "--with-zlib",
            "--with-ncurses",           # terminal UI (ncursesw via PKG_CONFIG_PATH)
            "--disable-build-details",  # reproducible build (no timestamp)
            "--with-native-compilation=aot", 
        ]
