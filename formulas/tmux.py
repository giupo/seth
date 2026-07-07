from seth.formula import Formula


class TmuxFormula(Formula):
    name = "tmux"
    latest = "3.5a"
    dependencies = ["libevent", "ncurses"]

    versions = {
        "3.5a": {
            "url": "https://github.com/tmux/tmux/releases/download/3.5a/tmux-3.5a.tar.gz",
            "sha256": "",  # sha256sum tmux-3.5a.tar.gz
        },
        "3.4": {
            "url": "https://github.com/tmux/tmux/releases/download/3.4/tmux-3.4.tar.gz",
            "sha256": "",
        },
    }

    def configure_args(self):
        from seth.config import config
        libevent_ver = self.direct_deps.get("libevent", "")
        libevent_prefix = config.cellar / "libevent" / libevent_ver
        return [
            f"--prefix={self.keg}",
            f"--with-libevent={libevent_prefix}",
            "--enable-utf8proc=no",
        ]
