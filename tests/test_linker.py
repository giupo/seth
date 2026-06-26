from __future__ import annotations

import pytest

from seth import linker
from seth.formula import Formula


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_keg(keg_root, name, version, files):
    """Create a fake keg directory tree with the given relative file paths."""
    keg = keg_root / name / version
    for rel in files:
        p = keg / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"content of {rel}")
    return keg


def _formula(isolated_config, name, version, keg):
    f = Formula()
    f.name = name
    f.version = version
    # Override the keg property by storing directly on the instance
    type(f).keg = property(lambda self: keg)
    return f


# ── link ──────────────────────────────────────────────────────────────────────

def test_link_creates_symlinks(isolated_config, tmp_path):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["bin/pkg", "lib/libpkg.so"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linked = linker.link(f)
    root = isolated_config.root
    assert (root / "bin" / "pkg").is_symlink()
    assert (root / "lib" / "libpkg.so").is_symlink()


def test_link_returns_relative_paths(isolated_config, tmp_path):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["bin/pkg"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linked = linker.link(f)
    assert "bin/pkg" in linked


def test_link_symlink_points_to_keg_file(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["bin/pkg"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linker.link(f)
    target = isolated_config.root / "bin" / "pkg"
    assert target.readlink() == keg / "bin" / "pkg"


def test_link_raises_on_conflict_without_force(isolated_config):
    keg1 = _make_keg(isolated_config.cellar, "a", "1.0", ["bin/tool"])
    keg2 = _make_keg(isolated_config.cellar, "b", "1.0", ["bin/tool"])
    fa = _formula(isolated_config, "a", "1.0", keg1)
    fb = _formula(isolated_config, "b", "1.0", keg2)
    linker.link(fa)
    with pytest.raises(FileExistsError, match="Conflicts found"):
        linker.link(fb)


def test_link_force_overwrites_symlink(isolated_config):
    keg1 = _make_keg(isolated_config.cellar, "a", "1.0", ["bin/tool"])
    keg2 = _make_keg(isolated_config.cellar, "b", "1.0", ["bin/tool"])
    fa = _formula(isolated_config, "a", "1.0", keg1)
    fb = _formula(isolated_config, "b", "1.0", keg2)
    linker.link(fa)
    linker.link(fb, force=True)   # should not raise
    target = isolated_config.root / "bin" / "tool"
    assert target.readlink() == keg2 / "bin" / "tool"


def test_link_raises_on_missing_keg(isolated_config):
    f = Formula()
    f.name = "ghost"
    f.version = "1.0"
    with pytest.raises(FileNotFoundError, match="Keg not found"):
        linker.link(f)


def test_link_creates_parent_directories(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["share/man/man1/pkg.1"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linker.link(f)
    assert (isolated_config.root / "share" / "man" / "man1" / "pkg.1").is_symlink()


def test_link_skips_aggregate_files(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0",
                    ["bin/pkg", "share/info/dir"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linked = linker.link(f)
    assert "share/info/dir" not in linked
    assert "bin/pkg" in linked


# ── unlink ────────────────────────────────────────────────────────────────────

def test_unlink_removes_symlinks(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["bin/pkg", "lib/libpkg.so"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linked = linker.link(f)
    linker.unlink(linked)
    root = isolated_config.root
    assert not (root / "bin" / "pkg").exists()
    assert not (root / "lib" / "libpkg.so").exists()


def test_unlink_removes_empty_parent_dirs(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["lib/pkgconfig/pkg.pc"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linked = linker.link(f)
    linker.unlink(linked)
    # lib/pkgconfig should be gone (was only created for this package)
    assert not (isolated_config.root / "lib" / "pkgconfig").exists()


def test_unlink_is_idempotent(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["bin/pkg"])
    f = _formula(isolated_config, "pkg", "1.0", keg)
    linked = linker.link(f)
    linker.unlink(linked)
    linker.unlink(linked)   # second call should not raise


def test_unlink_ignores_non_symlink_entries(isolated_config):
    # If a path in the list is not a symlink (e.g. was already cleaned up), skip it.
    linker.unlink(["bin/nonexistent"])   # should not raise


# ── scan_keg_files ────────────────────────────────────────────────────────────

def test_scan_keg_files_returns_relative_paths(isolated_config):
    keg = _make_keg(isolated_config.cellar, "pkg", "1.0", ["bin/pkg", "lib/libpkg.so"])
    paths = linker.scan_keg_files(keg)
    assert set(paths) == {"bin/pkg", "lib/libpkg.so"}


def test_scan_keg_files_empty_on_missing_keg(isolated_config):
    missing = isolated_config.cellar / "ghost" / "1.0"
    assert linker.scan_keg_files(missing) == []
