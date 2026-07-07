from seth.formula import Formula


class PythonFormula(Formula):
    name = "python"
    latest = "3.14.6"
 
    dependencies = ["xz", "libztsd", "libffi"]
    
    versions = {
        "3.14.6": {
            "url": "https://www.python.org/ftp/python/3.14.6/Python-3.14.6.tar.xz",
            "sha256": "143b1dddefaec3bd2e21e3b839b34a2b7fb9842272883c576420d605e9f30c63",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
            # "--enable-optimizations",
            "--with-lto",
        ]

    # def make_args(self):
    #     return [
    #         "PROFILE_TASK='-m test --pgo --timeout=$(TESTTIMEOUT) -x test_json'",
    #     ]
