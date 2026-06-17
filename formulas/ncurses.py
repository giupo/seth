from pathlib import Path

from seth.formula import Formula


class NcursesFormula(Formula):
    name = "ncurses"
    latest = "6.5"

    versions = {
        "6.5": {
            "url": "https://ftp.gnu.org/gnu/ncurses/ncurses-6.5.tar.gz",
            "sha256": "136d91bc269a9a5785e5f9e980bc76ab57428f604ce3e5a5a90cebc767971cc6",
        },
        "6.4": {
            "url": "https://ftp.gnu.org/gnu/ncurses/ncurses-6.4.tar.gz",
            "sha256": "6931283d9ac87c5073f30b6290c4c75f21632bb4fc3603ac8100812bed248159",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--with-shared",            # build .so
            "--with-cxx-shared",        # C++ binding .so
            "--without-normal",         # skip static .a (speeds up build)
            "--enable-widec",           # wide-char (libncursesw) — required by emacs
            "--enable-pc-files",        # install pkg-config .pc files
            f"--with-pkg-config-libdir={self.keg}/lib/pkgconfig",
            "--disable-stripping",      # let the linker strip if needed
            "--enable-symlinks",
        ]

    def post_install(self):
        """Create non-widec compat symlinks (libncurses → libncursesw).

        Many programs probe for -lncurses without knowing about the widec
        split; pointing them at the widec library is safe and correct.
        """
        lib = self.keg / "lib"
        pc = self.keg / "lib" / "pkgconfig"

        for stem in ("ncurses", "form", "menu", "panel"):
            widec = f"lib{stem}w.so"
            compat = lib / f"lib{stem}.so"
            if (lib / widec).exists() and not compat.exists():
                compat.symlink_to(widec)

        # ncurses.pc → ncursesw.pc so pkg-config ncurses also works
        compat_pc = pc / "ncurses.pc"
        if (pc / "ncursesw.pc").exists() and not compat_pc.exists():
            compat_pc.symlink_to("ncursesw.pc")
