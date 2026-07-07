from seth.formula import Formula


class ImagemagickFormula(Formula):
    name = "imagemagick"
    latest = "7.1.2-25"
    dependencies = ["zlib"]
    build_dependencies = ["pkgconfig"]

    versions = {
        "7.1.2-25": {
            "url": "https://imagemagick.org/archive/ImageMagick-7.1.2-25.tar.gz",
            "sha256": "c4ce2d982fbedf0347aeca804326308311d767c8da6a69e91ed39371f8de137b"
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            "--enable-shared",
            "--disable-static",
            "--without-x",          # no X11 — headless/server build
            "--with-zlib=yes",
            "--without-bzlib",      # skip bzip2 unless formula added
            "--without-lzma",
            "--without-png",        # skip unless libpng formula added
            "--without-jpeg",       # skip unless libjpeg formula added
            "--without-tiff",
            "--without-freetype",
            "--without-openmp",
            "--disable-docs",
        ]
