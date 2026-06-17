"""Download, verify, extract, and build a formula."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from .config import config
from .formula import Formula


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def download(formula: Formula) -> Path:
    config.downloads.mkdir(parents=True, exist_ok=True)
    filename = formula.url.split("/")[-1]
    dest = config.downloads / filename
    if dest.exists():
        print(f"  [cache] {filename}")
        return dest
    print(f"  [download] {formula.url}")
    urllib.request.urlretrieve(formula.url, dest)
    return dest


def verify(archive: Path, expected_sha256: str):
    if not expected_sha256:
        print("  [warn] no sha256 specified, skipping checksum")
        return
    print(f"  [verify] sha256 {archive.name}")
    actual = _sha256(archive)
    if actual != expected_sha256:
        raise ValueError(
            f"Checksum mismatch for {archive.name}\n"
            f"  expected: {expected_sha256}\n"
            f"  actual:   {actual}"
        )


def extract(archive: Path, build_dir: Path) -> Path:
    print(f"  [extract] {archive.name}")
    build_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as tf:
        tf.extractall(build_dir, filter="data")
    entries = list(build_dir.iterdir())
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return build_dir


def _run(cmd: list[str], cwd: Path):
    print(f"  [run] {' '.join(str(c) for c in cmd)}")
    print(f"        (cwd: {cwd})")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {' '.join(str(c) for c in cmd)}"
        )


def build(formula: Formula, source_dir: Path):
    formula.keg.mkdir(parents=True, exist_ok=True)
    system = formula.build_system

    if system == "autoconf":
        _run(["./configure"] + formula.configure_args(), cwd=source_dir)
        _run(["make", f"-j{_nproc()}"], cwd=source_dir)
        _run(["make", "install"], cwd=source_dir)

    elif system == "cmake":
        build_subdir = source_dir / "_build"
        build_subdir.mkdir(exist_ok=True)
        _run(["cmake", ".."] + formula.cmake_args(), cwd=build_subdir)
        _run(["make", f"-j{_nproc()}"], cwd=build_subdir)
        _run(["make", "install"], cwd=build_subdir)

    elif system == "meson":
        build_subdir = source_dir / "_build"
        _run(["meson", "setup", str(build_subdir)] + formula.meson_args(), cwd=source_dir)
        _run(["ninja", "-C", str(build_subdir)], cwd=source_dir)
        _run(["ninja", "-C", str(build_subdir), "install"], cwd=source_dir)

    elif system == "custom":
        formula.build(source_dir)

    else:
        raise ValueError(f"Unknown build_system: {system!r}")


def _build_tmpdir(formula: Formula) -> Path:
    # Use $TEMP if set, otherwise let tempfile pick the system default.
    base = os.environ.get("TEMP") or None
    return Path(tempfile.mkdtemp(prefix=f"seth.{formula.name}.{formula.version}.", dir=base))


def install(formula: Formula, debug: bool = False):
    """Full pipeline: download → verify → extract → build → post_install.

    The build tree lives in a fresh temp directory under $TEMP (or the
    system default when $TEMP is not set).  On failure it is always
    preserved so the user can inspect it.  With --debug it is preserved
    even on success.
    """
    print(f"==> Installing {formula.name} {formula.version}")

    archive = download(formula)
    verify(archive, formula.sha256)

    build_dir = _build_tmpdir(formula)
    source_dir = extract(archive, build_dir)
    print(f"  [build dir] {source_dir}")
    print(f"  [build] {formula.build_system}")

    try:
        build(formula, source_dir)
        formula.post_install()
    except Exception as exc:
        print(f"\nseth: build failed: {exc}")
        print(f"      build directory preserved at:")
        print(f"      {source_dir}")
        print(f"      cd '{source_dir}'")
        raise

    if debug:
        print(f"  [debug] build directory preserved at:")
        print(f"          {source_dir}")
    else:
        shutil.rmtree(build_dir, ignore_errors=True)

    print(f"==> {formula.name} {formula.version} installed to {formula.keg}")


def _nproc() -> int:
    import os
    return os.cpu_count() or 1
