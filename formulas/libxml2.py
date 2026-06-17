from seth.formula import Formula


class Libxml2Formula(Formula):
    name = "libxml2"
    latest = "2.12.9"
    dependencies = ["zlib"]

    versions = {
        "2.12.9": {
            "url": "https://download.gnome.org/sources/libxml2/2.12/libxml2-2.12.9.tar.xz",
            "sha256": "59912db536ab56a3996489ea0299768c7bcffe9c9a3f3ba68088e8a7b4f2c2b0",
        },
        "2.11.8": {
            "url": "https://download.gnome.org/sources/libxml2/2.11/libxml2-2.11.8.tar.xz",
            "sha256": "d3b9d6da8e26a27ee7bcd00d5d0800ece475b7fdecef06ef49a6b7d6ae5dfae5",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--without-python",   # avoid pulling in system python headers
            "--with-zlib",        # found via LDFLAGS/CPPFLAGS from get_build_env()
        ]
