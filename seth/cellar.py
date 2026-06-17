"""Cellar: tracks installed kegs in a JSON database."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import config


def _load_db() -> dict:
    if config.db_path.exists():
        return json.loads(config.db_path.read_text())
    return {}


def _save_db(db: dict):
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    config.db_path.write_text(json.dumps(db, indent=2))


def record_install(name: str, version: str, keg: Path):
    db = _load_db()
    db[name] = {
        "version": version,
        "keg": str(keg),
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "linked": False,
    }
    _save_db(db)


def record_link(name: str, linked: bool):
    db = _load_db()
    if name in db:
        db[name]["linked"] = linked
        _save_db(db)


def record_uninstall(name: str):
    db = _load_db()
    db.pop(name, None)
    _save_db(db)


def get_info(name: str) -> dict | None:
    return _load_db().get(name)


def list_installed() -> dict:
    return _load_db()


def is_installed(name: str) -> bool:
    return name in _load_db()


def installed_version(name: str) -> str | None:
    entry = _load_db().get(name)
    return entry["version"] if entry else None
