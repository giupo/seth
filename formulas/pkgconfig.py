from pathlib import Path

from seth.formula import Formula


class PkgConfigFormula(Formula):
    name = "pkgconfig"
    latest = "0.29.2"

    versions = {
        "0.29.2": {
            "url": "https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz",
            "sha256": "6fc69c01688c9458a57eb9a1664c9aba372ccda420a02bf4429fe610e7e7d591",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--with-internal-glib",
        ]

    def patch(self, source_dir: Path):
        # glib/goption.c uses 'bool' as a variable name and struct member, which
        # conflicts with the C99 keyword introduced via <stdbool.h>.  Rename to
        # '_bool' throughout that file so it compiles cleanly with gcc >= 8.
        goption = source_dir / "glib" / "goption.c"
        if not goption.exists():
            return
        text = goption.read_text()
        text = (text
                .replace("gboolean bool;",   "gboolean _bool;")
                .replace("->prev.bool",       "->prev._bool")
                .replace(".prev.bool",        ".prev._bool"))
        goption.write_text(text)
