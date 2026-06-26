import hashlib
import tarfile
import zipfile

import pytest

from seth import builder
from seth.formula import Formula
from seth.types import BuildType


# ── get_build_env ────────────────────────────────────────────────────────────

def test_get_build_env_prepends_root_paths(isolated_config):
    env = builder.get_build_env()
    root = isolated_config.root
    assert str(root / "bin") in env["PATH"]
    assert str(root / "lib" / "pkgconfig") in env["PKG_CONFIG_PATH"]
    assert f"-L{root}/lib" in env["LDFLAGS"]
    assert f"-I{root}/include" in env["CPPFLAGS"]


def test_get_build_env_with_direct_deps_prepends_dep_keg(isolated_config):
    dep_keg = isolated_config.cellar / "openssl" / "3.3.2"
    dep_keg.mkdir(parents=True)
    env = builder.get_build_env({"openssl": "3.3.2"})
    assert str(dep_keg / "lib") in env["LDFLAGS"]
    assert str(dep_keg / "include") in env["CPPFLAGS"]
    assert str(dep_keg / "lib") in env["LIBRARY_PATH"]
    # dep keg paths must appear before the global root paths
    ldflags = env["LDFLAGS"]
    assert ldflags.index(str(dep_keg / "lib")) < ldflags.index(str(isolated_config.root / "lib"))


def test_get_build_env_does_not_prepend_to_ld_library_path(isolated_config, monkeypatch):
    # Deliberately excluded: it would make build tools pick up seth's own
    # libs instead of the system ones they were compiled against.
    monkeypatch.delenv("LD_LIBRARY_PATH", raising=False)
    env = builder.get_build_env()
    assert "LD_LIBRARY_PATH" not in env


# ── _sha256 / verify ─────────────────────────────────────────────────────────

def test_sha256_matches_hashlib(tmp_path):
    p = tmp_path / "f.txt"
    p.write_bytes(b"hello world")
    assert builder._sha256(p) == hashlib.sha256(b"hello world").hexdigest()


def test_verify_passes_on_matching_checksum(tmp_path):
    p = tmp_path / "f.txt"
    p.write_bytes(b"hello world")
    builder.verify(p, hashlib.sha256(b"hello world").hexdigest())


def test_verify_raises_on_mismatch(tmp_path):
    p = tmp_path / "f.txt"
    p.write_bytes(b"hello world")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        builder.verify(p, "deadbeef")


def test_verify_skips_when_no_sha256_given(tmp_path):
    p = tmp_path / "f.txt"
    p.write_bytes(b"hello world")
    builder.verify(p, "")  # should not raise


# ── extract ──────────────────────────────────────────────────────────────────

def test_extract_returns_single_top_level_dir(tmp_path):
    src_dir = tmp_path / "pkg-1.0"
    src_dir.mkdir()
    (src_dir / "file.txt").write_text("hi")

    archive = tmp_path / "pkg-1.0.tar.gz"
    with tarfile.open(archive, "w:gz") as tf:
        tf.add(src_dir, arcname="pkg-1.0")

    build_dir = tmp_path / "build"
    result = builder.extract(archive, build_dir)
    assert result == build_dir / "pkg-1.0"
    assert (result / "file.txt").exists()


def test_extract_zip_returns_single_top_level_dir(tmp_path):
    archive = tmp_path / "pkg-1.0.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("pkg-1.0/file.txt", "hi")

    build_dir = tmp_path / "build"
    result = builder.extract(archive, build_dir)
    assert result == build_dir / "pkg-1.0"
    assert (result / "file.txt").exists()


def test_extract_copies_non_tarball_as_is(tmp_path):
    archive = tmp_path / "raw_script.sh"
    archive.write_text("#!/bin/sh\necho hi\n")

    build_dir = tmp_path / "build"
    result = builder.extract(archive, build_dir)
    assert result == build_dir
    assert (build_dir / "raw_script.sh").exists()


# ── _run ─────────────────────────────────────────────────────────────────────

def test_run_raises_on_nonzero_exit(tmp_path):
    with pytest.raises(RuntimeError, match="exit 1"):
        builder._run(["sh", "-c", "exit 1"], cwd=tmp_path)


def test_run_succeeds_on_zero_exit(tmp_path):
    builder._run(["sh", "-c", "exit 0"], cwd=tmp_path)  # should not raise


# ── build() dispatch ─────────────────────────────────────────────────────────

class _RecordingFormula(Formula):
    name = "pkg"
    version = "1.0"

    def __init__(self, build_system):
        self.build_system = build_system


@pytest.fixture
def recorded_cmds(monkeypatch):
    calls = []

    def fake_run(cmd, cwd, env=None):
        calls.append(list(cmd))

    monkeypatch.setattr(builder, "_run", fake_run)
    return calls


def test_build_autoconf_runs_configure_then_make(isolated_config, tmp_path, recorded_cmds):
    f = _RecordingFormula(BuildType.AUTOCONF)
    builder.build(f, tmp_path)
    assert recorded_cmds[0][0] == "./configure"
    assert recorded_cmds[1][:2] == ["make", f"-j{builder._nproc()}"]
    assert recorded_cmds[2] == ["make", "install"]


def test_build_make_skips_configure(isolated_config, tmp_path, recorded_cmds):
    f = _RecordingFormula(BuildType.MAKE)
    builder.build(f, tmp_path)
    assert all(cmd[0] != "./configure" for cmd in recorded_cmds)
    assert recorded_cmds[0][:2] == ["make", f"-j{builder._nproc()}"]
    assert recorded_cmds[1] == ["make", "install"]


def test_build_make_passes_extra_make_args(isolated_config, tmp_path, recorded_cmds):
    f = _RecordingFormula(BuildType.MAKE)
    f.extra_make_args = [f"PREFIX={f.keg}"]
    builder.build(f, tmp_path)
    assert f"PREFIX={f.keg}" in recorded_cmds[0]
    assert f"PREFIX={f.keg}" in recorded_cmds[1]


def test_build_cmake_runs_cmake_then_make_in_subdir(isolated_config, tmp_path, recorded_cmds):
    f = _RecordingFormula(BuildType.CMAKE)
    builder.build(f, tmp_path)
    assert recorded_cmds[0][0] == "cmake"
    assert (tmp_path / "_build").is_dir()


def test_build_meson_runs_meson_then_ninja(isolated_config, tmp_path, recorded_cmds):
    f = _RecordingFormula(BuildType.MESON)
    builder.build(f, tmp_path)
    assert recorded_cmds[0][:2] == ["meson", "setup"]
    assert recorded_cmds[1][0] == "ninja"
    assert recorded_cmds[2][:2] == ["ninja", "-C"] or "install" in recorded_cmds[2]


def test_build_custom_delegates_to_formula_build(isolated_config, tmp_path):
    called = {}

    class CustomFormula(_RecordingFormula):
        def build(self, source_dir):
            called["source_dir"] = source_dir

    f = CustomFormula(BuildType.CUSTOM)
    builder.build(f, tmp_path)
    assert called["source_dir"] == tmp_path


def test_build_unknown_system_raises(isolated_config, tmp_path):
    f = _RecordingFormula("not-a-real-system")
    with pytest.raises(ValueError, match="Unknown build_system"):
        builder.build(f, tmp_path)
