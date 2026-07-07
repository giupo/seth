from pathlib import Path

from seth.formula import Formula


class PkgConfigFormula(Formula):
    name = "pkgconfig"
    latest = "0.29.2"
    dependencies = ["glib"]
    
    versions = {
        "0.29.2": {
            "url": "https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz",
            "sha256": "6fc69c01688c9458a57eb9a1664c9aba372ccda420a02bf4429fe610e7e7d591",
        },
    }

    def configure_args(self):
        return [
            f"--prefix={self.keg}",
        ]

