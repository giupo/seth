from seth.formula import Formula


class ImagemagickFormula(Formula):
    name = "imagemagick"
    latest = "7.1.1-47"
    dependencies = ["zlib"]
    build_dependencies = ["pkgconfig"]

    versions = {
        "7.1.1-47": {
            "url": "https://imagemagick.org/archive/ImageMagick-7.1.1-47.tar.gz",
            "sha256": "",  # sha256sum ImageMagick-7.1.1-47.tar.gz
        },
        "7.1.1-38": {
            "url": "https://imagemagick.org/archive/ImageMagick-7.1.1-38.tar.gz",
            "sha256": "",
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
