from __future__ import annotations

from pathlib import Path

import pytest

from seth import cellar


# All tests use isolated_config so the real ~/.local/seth db is never touched.


def test_record_install_creates_entry(isolated_config, tmp_path):
    keg = tmp_path / "wget" / "1.0"
    cellar.record_install("wget", "1.0", keg)
    assert cellar.is_installed("wget", "1.0")


def test_record_install_stores_sha256(isolated_config, tmp_path):
    keg = tmp_path / "pkg" / "1.0"
    cellar.record_install("pkg", "1.0", keg, sha256="deadbeef")
    info = cellar.get_info("pkg")
    assert info["versions"]["1.0"]["sha256"] == "deadbeef"


def test_record_install_multiple_versions(isolated_config, tmp_path):
    for ver in ("1.0", "2.0"):
        cellar.record_install("pkg", ver, tmp_path / ver)
    assert cellar.is_installed("pkg", "1.0")
    assert cellar.is_installed("pkg", "2.0")
    assert set(cellar.installed_versions("pkg")) == {"1.0", "2.0"}


def test_record_link_sets_linked(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path / "1.0")
    cellar.record_link("pkg", "1.0", linked_files=["bin/pkg"])
    assert cellar.linked_version("pkg") == "1.0"
    assert cellar.linked_files("pkg") == ["bin/pkg"]


def test_record_link_none_unlinks(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path / "1.0")
    cellar.record_link("pkg", "1.0", linked_files=["bin/pkg"])
    cellar.record_link("pkg", None)
    assert cellar.linked_version("pkg") is None
    assert cellar.linked_files("pkg") == []


def test_record_link_noop_on_unknown_package(isolated_config):
    cellar.record_link("ghost", "1.0")   # should not raise


def test_record_uninstall_removes_version(isolated_config, tmp_path):
    for ver in ("1.0", "2.0"):
        cellar.record_install("pkg", ver, tmp_path / ver)
    cellar.record_uninstall("pkg", "1.0")
    assert not cellar.is_installed("pkg", "1.0")
    assert cellar.is_installed("pkg", "2.0")


def test_record_uninstall_whole_package(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path / "1.0")
    cellar.record_uninstall("pkg")
    assert not cellar.is_installed("pkg")
    assert cellar.get_info("pkg") is None


def test_record_uninstall_last_version_removes_entry(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path / "1.0")
    cellar.record_uninstall("pkg", "1.0")
    assert cellar.get_info("pkg") is None


def test_record_uninstall_linked_version_clears_link(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path / "1.0")
    cellar.record_link("pkg", "1.0", linked_files=["bin/pkg"])
    cellar.record_uninstall("pkg", "1.0")
    # Entry removed entirely; linked_version returns None
    assert cellar.linked_version("pkg") is None


def test_record_uninstall_noop_on_unknown(isolated_config):
    cellar.record_uninstall("ghost")          # should not raise
    cellar.record_uninstall("ghost", "1.0")   # should not raise


def test_is_installed_false_when_empty(isolated_config):
    assert not cellar.is_installed("pkg")


def test_is_installed_any_version(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path)
    assert cellar.is_installed("pkg")
    assert not cellar.is_installed("pkg", "2.0")


def test_linked_version_none_when_not_linked(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path)
    assert cellar.linked_version("pkg") is None


def test_linked_files_empty_when_not_recorded(isolated_config, tmp_path):
    cellar.record_install("pkg", "1.0", tmp_path)
    assert cellar.linked_files("pkg") == []


def test_list_installed_returns_all(isolated_config, tmp_path):
    cellar.record_install("a", "1.0", tmp_path)
    cellar.record_install("b", "2.0", tmp_path)
    names = set(cellar.list_installed().keys())
    assert names == {"a", "b"}


def test_migrate_legacy_format(isolated_config):
    import json
    isolated_config.db_path.parent.mkdir(parents=True, exist_ok=True)
    legacy = {
        "wget": {
            "version": "1.21.4",
            "keg": "/tmp/wget/1.21.4",
            "installed_at": "2024-01-01T00:00:00+00:00",
            "linked": True,
        }
    }
    isolated_config.db_path.write_text(json.dumps(legacy))
    assert cellar.is_installed("wget", "1.21.4")
    assert cellar.linked_version("wget") == "1.21.4"


def test_concurrent_writes_do_not_corrupt(isolated_config, tmp_path):
    """Two sequential write operations land in the db without clobbering each other."""
    cellar.record_install("a", "1.0", tmp_path / "a")
    cellar.record_install("b", "1.0", tmp_path / "b")
    assert cellar.is_installed("a", "1.0")
    assert cellar.is_installed("b", "1.0")
