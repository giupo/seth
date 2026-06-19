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
from enum import StrEnum

from . import colors as col
from .config import config
from .formula import Formula
from .types import BuildType


# ── build environment ─────────────────────────────────────────────────────────

def get_build_env() -> dict[str, str]:
    """Return a copy of the environment with the seth root paths prepended.

    Ensures that packages already installed in the seth root are visible
    to configure scripts, pkg-config, and the compiler during every build.
    Formula custom-build methods should call this instead of os.environ.copy().
    """
    env = os.environ.copy()
    root = config.root

    def prepend_path(key: str, *dirs):
        new = ":".join(str(d) for d in dirs)
        old = env.get(key, "")
        env[key] = f"{new}:{old}" if old else new

    def prepend_flags(key: str, *flags):
        new = " ".join(flags)
        old = env.get(key, "")
        env[key] = f"{new} {old}" if old else new

    prepend_path("PATH",            root / "bin", root / "sbin")
    prepend_path("PKG_CONFIG_PATH", root / "lib" / "pkgconfig",
                                    root / "share" / "pkgconfig")
    # LIBRARY_PATH is the compile-time library search path (used by gcc -l).
    # LD_LIBRARY_PATH is intentionally NOT set here: it affects runtime library
    # loading for every process spawned during the build — including system tools
    # like cc1, ld, perl — which would then pick up seth's libgmp/libmpfr/libmpc
    # instead of the system versions they were compiled against, causing crashes.
    # Instead we embed RPATH directly in the binaries we produce via -Wl,-rpath.
    prepend_path("LIBRARY_PATH",    root / "lib", root / "lib64")
    prepend_path("ACLOCAL_PATH",    root / "share" / "aclocal")
    prepend_flags("LDFLAGS",
                  f"-L{root}/lib", f"-L{root}/lib64",
                  f"-Wl,-rpath,{root}/lib",
                  f"-Wl,-rpath,{root}/lib64")
    prepend_flags("CPPFLAGS", f"-I{root}/include")

    return env


# ── helpers ───────────────────────────────────────────────────────────────────

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
        print(f"  {col.tag('cached')}{col.dim(filename)}")
        return dest
    print(f"  {col.tag('download')}{formula.url}")
    urllib.request.urlretrieve(formula.url, dest)
    return dest


def verify(archive: Path, expected_sha256: str):
    if not expected_sha256:
        print(f"  {col.tag('warn')}{col.yellow('no sha256 specified, skipping checksum')}")
        return
    print(f"  {col.tag('verify')}sha256 {archive.name}")
    actual = _sha256(archive)
    if actual != expected_sha256:
        raise ValueError(
            f"Checksum mismatch for {archive.name}\n"
            f"  expected: {expected_sha256}\n"
            f"  actual:   {actual}"
        )


def extract(archive: Path, build_dir: Path) -> Path:
    print(f"  {col.tag('extract')}{archive.name}")
    build_dir.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(archive) as tf:
            tf.extractall(build_dir, filter="data")
            entries = list(build_dir.iterdir())
            if len(entries) == 1 and entries[0].is_dir():
                return entries[0]
    except Exception as e:
        print(f"  {col.tag('error')} {e}")
        print(f"  {col.tag('warn')} can't decompress {archive}, assume it's a file ...")
        shutil.copy2(archive, build_dir)

        
    return build_dir


def _run(cmd: list[str], cwd: Path, env: dict | None = None):
    if env is None:
        env = get_build_env()
    cmd_str = " ".join(str(c) for c in cmd)
    print(f"  {col.tag('run')}{col.dim(cmd_str)}")
    print(f"  {' ' * 11}{col.dim(f'(cwd: {cwd})')}")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {cmd_str}"
        )


def apply_patches(formula: Formula, source_dir: Path):
    from .formula import Formula as _Base, _find_patch_file
    for patch_file in formula.patches:
        path = _find_patch_file(formula.name, patch_file)
        print(f"  {col.tag('patch')}{col.dim(patch_file)}")
        _run(["patch", "-p1", "--input", str(path)], cwd=source_dir)
    if type(formula).patch is not _Base.patch:
        print(f"  {col.tag('patch')}{col.dim('source patch')}")
        formula.patch(source_dir)


def build(formula: Formula, source_dir: Path):
    formula.keg.mkdir(parents=True, exist_ok=True)
    env = get_build_env()
    system = formula.build_system
    apply_patches(formula, source_dir)

    if system == BuildType.AUTOGEN:
        _run(["./autogen.sh"], cwd=source_dir, env=env)
        _run(["./configure"] + formula.configure_args(), cwd=source_dir, env=env)
        _run(["make", f"-j{_nproc()}"] + formula.make_args(), cwd=source_dir, env=env)
        _run(["make", "install"] + formula.make_args(), cwd=source_dir, env=env)
    
    elif system == BuildType.AUTOCONF:
        _run(["./configure"] + formula.configure_args(), cwd=source_dir, env=env)
        _run(["make", f"-j{_nproc()}"] + formula.make_args(), cwd=source_dir, env=env)
        _run(["make", "install"] + formula.make_args(), cwd=source_dir, env=env)

    elif system == BuildType.CMAKE:
        # No configure step: bare Makefile projects (e.g. bzip2) that take
        # their settings (PREFIX, CC, ...) as make variables instead.
        _run(["make", f"-j{_nproc()}"] + formula.make_args(), cwd=source_dir, env=env)
        _run(["make", "install"] + formula.make_args(), cwd=source_dir, env=env)

    elif system == BuildType.CMAKE:
        build_subdir = source_dir / "_build"
        build_subdir.mkdir(exist_ok=True)
        _run(["cmake", ".."] + formula.cmake_args(), cwd=build_subdir, env=env)
        _run(["make", f"-j{_nproc()}"] + formula.make_args(), cwd=build_subdir, env=env)
        _run(["make", "install"] + formula.make_args(), cwd=build_subdir, env=env)

    elif system == BuildType.MESON:
        build_subdir = source_dir / "_build"
        _run(["meson", "setup", str(build_subdir)] + formula.meson_args(),
             cwd=source_dir, env=env)
        _run(["ninja", "-C", str(build_subdir)], cwd=source_dir, env=env)
        _run(["ninja", "-C", str(build_subdir), "install"], cwd=source_dir, env=env)

    elif system == BuildType.CUSTOM:
        formula.build(source_dir)

    else:
        raise ValueError(f"Unknown build_system: {system!r}")


def _build_tmpdir(formula: Formula) -> Path:
    return Path(
        tempfile.mkdtemp(
            prefix=f"seth.{formula.name}.{formula.version}.",
            dir=config.tmp_dir
        )
    )


def install(formula: Formula, debug: bool = False):
    """Full pipeline: download → verify → extract → build → post_install."""
    print(col.header(f"Installing {col.pkg(formula.name, formula.version)}"))

    archive = download(formula)
    verify(archive, formula.sha256)

    build_dir = _build_tmpdir(formula)
    source_dir = extract(archive, build_dir)
    print(f"  {col.tag('build dir')}{col.dim(str(source_dir))}")
    print(f"  {col.tag('build')}{col.bold(formula.build_system)}")

    try:
        build(formula, source_dir)
        formula.post_install()
    except Exception as exc:
        print(f"\n{col.b_red('Build failed:')} {exc}", flush=True)
        print(f"  {col.yellow('build directory preserved at:')}")
        print(f"  {col.dim(str(source_dir))}")
        print(f"  {col.dim(repr('cd ' + str(source_dir)))}")
        raise

    if debug:
        print(f"  {col.tag('debug')}{col.magenta('build directory preserved at:')}")
        print(f"  {col.dim(str(source_dir))}")
    else:
        shutil.rmtree(build_dir, ignore_errors=True)

    print(col.header(
        f"{col.pkg(formula.name, formula.version)} installed to "
        f"{col.dim(str(formula.keg))}"
    ))


def _nproc() -> int:
    return os.cpu_count() or 1
