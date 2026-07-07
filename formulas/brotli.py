from seth.formula import Formula


class BrotliFormula(Formula):
    name = "brotli"
    latest = "1.2.0"
    # dependencies = []
    # build_dependencies = []
    build_system = "cmake"
    
    versions = {
        "1.2.0": {
            "url": "https://github.com/google/brotli/archive/refs/tags/v1.2.0.tar.gz",
            "sha256": "816c96e8e8f193b40151dad7e8ff37b1221d019dbcb9c35cd3fadbfe6477dfec",
        },
    }

    def configure_args(self):
        return [
            "-DCMAKE_BUILD_TYPE=Release",
            f"-DCMAKE_INSTALL_PREFIX={self.keg}",
            "-DCMAKE_INSTALL_LIBDIR=lib",
            "-DBUILD_SHARED_LIBS=ON"
        ]


    
