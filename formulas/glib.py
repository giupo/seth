from pathlib import Path

from seth.formula import Formula


class GlibFormula(Formula):
    name = "glib"
    latest = "2.89.0"
    build_system = "meson"
    build_dependencies = ["ninja"]    
    dependencies = ["perl", "pcre2"]
    versions = {
        "2.89.0": {
            "url": "https://download.gnome.org/sources/glib/2.89/glib-2.89.0.tar.xz",
            "sha256": "205bf5dab175de68f11e33be7bb36d4ad4c5a5097d8c0c88a8682b257b6293dc",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--libdir=lib"
            "--buildtype=release",
            "-Ddefault_library=shared",
            "-Dintrospection=disabled",
            "-Ddocumentation=false",
            "-Dman-pages=disabled",
            "-Dtests=false",
            "-Dinstalled_tests=false",
            "-Dselinux=disabled",
            "-Dxattr=false",
            "-Ddtrace=disabled",
            "-Dsystemtap=disabled",
            "-Dsysprof=disabled",
            "-Dlibmount=disabled",
            "-Dnls=disabled",
        ]

