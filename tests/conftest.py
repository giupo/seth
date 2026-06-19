import pytest

from seth.config import config


@pytest.fixture
def isolated_config(tmp_path, monkeypatch):
    """Point the config singleton at a throwaway directory tree.

    config is a module-level singleton built at import time from env vars /
    a config file, so tests that touch paths must redirect its attributes
    rather than relying on the real user environment.
    """
    root = tmp_path / "seth-root"
    formulas_dir = tmp_path / "formulas"
    formulas_dir.mkdir()

    monkeypatch.setattr(config, "root", root)
    monkeypatch.setattr(config, "cellar", root / "Cellar")
    monkeypatch.setattr(config, "downloads", root / "Downloads")
    monkeypatch.setattr(config, "tmp_dir", str(tmp_path / "tmp"))
    monkeypatch.setattr(config, "formula_search_dirs", [formulas_dir])
    monkeypatch.setattr(config, "patch_dirs", [formulas_dir / "patches"])
    return config


@pytest.fixture
def formula_dir(isolated_config):
    """The single formula search directory set up by isolated_config."""
    return isolated_config.formula_search_dirs[0]
