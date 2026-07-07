from __future__ import annotations

import pytest

from seth import linker
from seth.formula import Formula


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_keg(isolated_config, name, version, files):
    """Create a fake keg at config.cellar/<name>/<version> with the given files."""
    keg = isolated_config.cellar / name / version
    for rel in files:
        p = keg / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"content of {rel}")
    return keg


def _formula(name, version):
    """Create a bare Formula instance with the given name and version.
    Formula.keg = config.cellar / name / version, so isolated_config must be
    active in the test for the keg to resolve to the temp directory.
    """
    f = Formula()
    f.name = name
    f.version = version
    return f


# ── link ──────────────────────────────────────────────────────────────────────

def test_link_creates_symlinks(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg", "lib/libpkg.so"])
    f = _formula("pkg", "1.0")
    linker.link(f)
    root = isolated_config.root
    assert (root / "bin" / "pkg").is_symlink()
    assert (root / "lib" / "libpkg.so").is_symlink()


def test_link_returns_relative_paths(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg"])
    f = _formula("pkg", "1.0")
    linked = linker.link(f)
    assert "bin/pkg" in linked


def test_link_symlink_points_to_keg_file(isolated_config):
    keg = _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg"])
    f = _formula("pkg", "1.0")
    linker.link(f)
    target = isolated_config.root / "bin" / "pkg"
    assert target.readlink() == keg / "bin" / "pkg"


def test_link_raises_on_conflict_without_force(isolated_config):
    _make_keg(isolated_config, "a", "1.0", ["bin/tool"])
    _make_keg(isolated_config, "b", "1.0", ["bin/tool"])
    fa = _formula("a", "1.0")
    fb = _formula("b", "1.0")
    linker.link(fa)
    with pytest.raises(FileExistsError, match="Conflicts found"):
        linker.link(fb)


def test_link_force_overwrites_symlink(isolated_config):
    keg_a = _make_keg(isolated_config, "a", "1.0", ["bin/tool"])
    keg_b = _make_keg(isolated_config, "b", "1.0", ["bin/tool"])
    fa = _formula("a", "1.0")
    fb = _formula("b", "1.0")
    linker.link(fa)
    linker.link(fb, force=True)   # should not raise
    target = isolated_config.root / "bin" / "tool"
    assert target.readlink() == keg_b / "bin" / "tool"


def test_link_raises_on_missing_keg(isolated_config):
    f = _formula("ghost", "1.0")
    # No keg created → config.cellar/ghost/1.0 does not exist
    with pytest.raises(FileNotFoundError, match="Keg not found"):
        linker.link(f)


def test_link_creates_parent_directories(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["share/man/man1/pkg.1"])
    f = _formula("pkg", "1.0")
    linker.link(f)
    assert (isolated_config.root / "share" / "man" / "man1" / "pkg.1").is_symlink()


def test_link_skips_aggregate_files(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg", "share/info/dir"])
    f = _formula("pkg", "1.0")
    linked = linker.link(f)
    assert "share/info/dir" not in linked
    assert "bin/pkg" in linked


# ── unlink ────────────────────────────────────────────────────────────────────

def test_unlink_removes_symlinks(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg", "lib/libpkg.so"])
    f = _formula("pkg", "1.0")
    linked = linker.link(f)
    linker.unlink(linked)
    root = isolated_config.root
    assert not (root / "bin" / "pkg").exists()
    assert not (root / "lib" / "libpkg.so").exists()


def test_unlink_removes_empty_parent_dirs(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["lib/pkgconfig/pkg.pc"])
    f = _formula("pkg", "1.0")
    linked = linker.link(f)
    linker.unlink(linked)
    assert not (isolated_config.root / "lib" / "pkgconfig").exists()


def test_unlink_is_idempotent(isolated_config):
    _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg"])
    f = _formula("pkg", "1.0")
    linked = linker.link(f)
    linker.unlink(linked)
    linker.unlink(linked)   # second call should not raise


def test_unlink_ignores_non_symlink_entries(isolated_config):
    linker.unlink(["bin/nonexistent"])   # should not raise


# ── scan_keg_files ────────────────────────────────────────────────────────────

def test_scan_keg_files_returns_relative_paths(isolated_config):
    keg = _make_keg(isolated_config, "pkg", "1.0", ["bin/pkg", "lib/libpkg.so"])
    paths = linker.scan_keg_files(keg)
    assert set(paths) == {"bin/pkg", "lib/libpkg.so"}


def test_scan_keg_files_empty_on_missing_keg(isolated_config):
    missing = isolated_config.cellar / "ghost" / "1.0"
    assert linker.scan_keg_files(missing) == []
