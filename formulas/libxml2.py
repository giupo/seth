from seth.formula import Formula


class Libxml2Formula(Formula):
    name = "libxml2"
    latest = "2.15.3"
    dependencies = ["zlib"]

    versions = {
        "2.15.3": {
            "url": "https://download.gnome.org/sources/libxml2/2.15/libxml2-2.15.3.tar.xz",
            "sha256": "78262a6e7ac170d6528ebfe2efccdf220191a5af6a6cd61ea4a9a9a5042c7a07"
        },
        "2.12.9": {
            "url": "https://download.gnome.org/sources/libxml2/2.12/libxml2-2.12.9.tar.xz",
            "sha256": "59912db536ab56a3996489ea0299768c7bcffe57169f0235e7f962a91f483590",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--without-python",   # avoid pulling in system python headers
            "--with-zlib",        # found via LDFLAGS/CPPFLAGS from get_build_env()
        ]
