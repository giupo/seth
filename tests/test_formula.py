import pytest

from seth.formula import (
    Formula,
    available_versions,
    list_available,
    load_formula,
)
from seth.types import BuildType


WGET_LIKE = '''
from seth.formula import Formula

class WgetFormula(Formula):
    name = "wget"
    latest = "1.21.4"
    dependencies = ["openssl"]

    versions = {
        "1.21.4": {"url": "https://example.org/wget-1.21.4.tar.gz", "sha256": "aaa"},
        "1.21.3": {"url": "https://example.org/wget-1.21.3.tar.gz", "sha256": "bbb"},
        "1.20.0": {
            "url": "https://example.org/wget-1.20.0.tar.gz",
            "sha256": "ccc",
            "configure_args": lambda self: [f"--prefix={self.keg}", "--legacy"],
        },
    }

    def configure_args(self):
        return [f"--prefix={self.keg}", "--with-ssl=openssl"]
'''

BZIP2_LIKE = '''
from seth.formula import Formula
from seth.types import BuildType

class Bzip2Formula(Formula):
    name = "bzip2"
    latest = "1.0.8"
    build_system = BuildType.MAKE

    versions = {
        "1.0.8": {"url": "https://example.org/bzip2-1.0.8.tar.gz", "sha256": "ddd"},
    }

    def make_args(self):
        return [f"PREFIX={self.keg}"]
'''


def write_formula(formula_dir, filename, content):
    (formula_dir / filename).write_text(content)


# ── Formula base class defaults ────────────────────────────────────────────

def test_default_build_system_is_autoconf():
    assert Formula().build_system == BuildType.AUTOCONF


def test_configure_args_default_includes_prefix_and_extra():
    f = Formula()
    f.name, f.version = "pkg", "1.0"
    f.extra_configure_args = ["--enable-shared"]
    args = f.configure_args()
    assert args[0] == f"--prefix={f.keg}"
    assert "--enable-shared" in args


def test_make_args_default_is_extra_make_args():
    f = Formula()
    f.extra_make_args = ["CFLAGS=-O2"]
    assert f.make_args() == ["CFLAGS=-O2"]


def test_make_args_default_empty():
    assert Formula().make_args() == []


def test_cmake_args_uses_cmake_install_prefix():
    f = Formula()
    f.name, f.version = "pkg", "1.0"
    assert f.cmake_args()[0] == f"-DCMAKE_INSTALL_PREFIX={f.keg}"


def test_meson_args_uses_prefix_flag():
    f = Formula()
    f.name, f.version = "pkg", "1.0"
    assert f.meson_args()[0] == f"--prefix={f.keg}"


def test_keg_path_is_cellar_name_version(isolated_config):
    f = Formula()
    f.name, f.version = "pkg", "2.0"
    assert f.keg == isolated_config.cellar / "pkg" / "2.0"


# ── load_formula ────────────────────────────────────────────────────────────

def test_load_formula_picks_latest_version(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    f = load_formula("wget")
    assert f.version == "1.21.4"
    assert f.url == "https://example.org/wget-1.21.4.tar.gz"
    assert f.sha256 == "aaa"


def test_load_formula_picks_specific_version(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    f = load_formula("wget", "1.21.3")
    assert f.version == "1.21.3"
    assert f.sha256 == "bbb"


def test_load_formula_applies_version_level_override(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    f = load_formula("wget", "1.20.0")
    assert f.configure_args() == [f"--prefix={f.keg}", "--legacy"]


def test_load_formula_default_configure_args_when_no_override(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    f = load_formula("wget", "1.21.4")
    assert f.configure_args() == [f"--prefix={f.keg}", "--with-ssl=openssl"]


def test_load_formula_unknown_version_raises(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    with pytest.raises(ValueError, match="not available"):
        load_formula("wget", "9.9.9")


def test_load_formula_missing_file_raises(formula_dir):
    with pytest.raises(FileNotFoundError):
        load_formula("does-not-exist")


def test_load_formula_make_build_system(formula_dir):
    write_formula(formula_dir, "bzip2.py", BZIP2_LIKE)
    f = load_formula("bzip2")
    assert f.build_system == BuildType.MAKE
    assert f.make_args() == [f"PREFIX={f.keg}"]


# ── available_versions / list_available ────────────────────────────────────

def test_available_versions_sorted_newest_first(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    assert available_versions("wget") == ["1.21.4", "1.21.3", "1.20.0"]


def test_list_available_lists_formula_names(formula_dir):
    write_formula(formula_dir, "wget.py", WGET_LIKE)
    write_formula(formula_dir, "bzip2.py", BZIP2_LIKE)
    assert sorted(list_available()) == ["bzip2", "wget"]
