from seth.formula import Formula


class EmacsFormula(Formula):
    name = "emacs"
    latest = "30.1"
    dependencies = ["ncurses", "libxml2", "gnutls", "zlib"]
    build_dependencies = ["pkgconfig"]

    versions = {
        "30.1": {
            "url": "https://ftp.gnu.org/gnu/emacs/emacs-30.1.tar.gz",
            "sha256": "eba816fb605c57ec785d14a9bff3d5abd69793d77af9a90c6c8862c44048ae64",
        },
        "29.4": {
            "url": "https://ftp.gnu.org/gnu/emacs/emacs-29.4.tar.gz",
            "sha256": "ba9e7d24fbe80e7b79e7b1abad6d84e7777d233940b9c126ad34eb3b7a09bc9b",
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
        ]
