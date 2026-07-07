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
            # GCC 14+ made implicit-function-declaration a hard error in every
            # -std mode (not just C23), which breaks ncurses' old K&R-style
            # configure checks/sources. -std=c99 does NOT fix this (verified);
            # only downgrading the diagnostic itself does.
            #
            # Also force pre-C23 dialect: GCC's default dialect is now C23,
            # where `bool` is a native keyword. ncurses' configure probes the
            # *C* compiler for a builtin bool without including <stdbool.h>;
            # under C23 that probe wrongly succeeds, so configure assumes "C
            # has bool" and disables the logic that makes the C++ binding use
            # the real C++ bool. The result is `#define bool NCURSES_BOOL`
            # (unsigned char) leaking into the C++ binding sources, which
            # breaks libstdc++'s C++20 concepts (same_as, is_object_v, ...)
            # when building c++/cursesapp.cc etc. -std=gnu17 restores the
            # pre-C23 probe result.
            "CFLAGS=-std=gnu17 -Wno-implicit-function-declaration",
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
