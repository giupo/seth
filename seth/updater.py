"""Fetch the remote formula repository (git or tar.gz)."""

from __future__ import annotations

import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from .config import config


def update():
    url = config.formulas_url
    if not url:
        raise ValueError(
            "No formulas URL configured.\n"
            "Add to ~/.config/seth/seth.conf:\n\n"
            "  [formulas]\n"
            "  url = https://example.com/seth-formulas/archive/main.tar.gz\n\n"
            "or set SETH_FORMULAS_URL."
        )

    dest = config.remote_formulas_dir
    print(f"==> Updating formulas from {url}")

    if _is_git_url(url):
        _git_update(url, dest)
    else:
        _tarball_update(url, dest)

    n = sum(1 for p in dest.glob("*.py") if p.stem != "__init__")
    print(f"==> {n} formulas available in {dest}")


def _is_git_url(url: str) -> bool:
    return url.endswith(".git") or (
        any(host in url for host in ("github.com", "gitlab.com", "bitbucket.org"))
        and not any(url.endswith(ext) for ext in (".tar.gz", ".tgz", ".zip"))
    )


def _git_update(url: str, dest: Path):
    git = shutil.which("git")
    if not git:
        raise RuntimeError("git not found in PATH; configure a tar.gz URL instead")

    if (dest / ".git").exists():
        print(f"  [git pull] {dest}")
        subprocess.run([git, "-C", str(dest), "pull", "--ff-only"], check=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  [git clone] {url}")
        subprocess.run([git, "clone", "--depth=1", url, str(dest)], check=True)


def _tarball_update(url: str, dest: Path):
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        print(f"  [download] {url}")
        urllib.request.urlretrieve(url, tmp_path)

        with tempfile.TemporaryDirectory() as td:
            print("  [extract]")
            with tarfile.open(tmp_path) as tf:
                tf.extractall(td, filter="data")

            # GitHub/GitLab archives wrap everything in a top-level directory.
            entries = list(Path(td).iterdir())
            src = entries[0] if len(entries) == 1 and entries[0].is_dir() else Path(td)

            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
    finally:
        tmp_path.unlink(missing_ok=True)
