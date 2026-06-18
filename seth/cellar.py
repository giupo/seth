"""Cellar: multi-version JSON database of installed kegs.

DB schema per package:
{
  "wget": {
    "versions": {
      "1.21.4": {"keg": "...", "installed_at": "..."},
      "1.21.3": {"keg": "...", "installed_at": "..."}
    },
    "linked": "1.21.4"   # null when nothing is linked
  }
}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .config import config


def _load_db() -> dict:
    if config.db_path.exists():
        return _migrate(json.loads(config.db_path.read_text()))
    return {}


def _migrate(raw: dict) -> dict:
    """Upgrade old single-version entries to the multi-version schema."""
    out = {}
    for name, entry in raw.items():
        if "versions" in entry:
            out[name] = entry
        else:
            ver = entry.get("version", "")
            out[name] = {
                "versions": {
                    ver: {
                        "keg": entry.get("keg", ""),
                        "installed_at": entry.get("installed_at", ""),
                    }
                },
                "linked": ver if entry.get("linked") else None,
            }
    return out


def _save_db(db: dict):
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    config.db_path.write_text(json.dumps(db, indent=2))


# ── write ────────────────────────────────────────────────────────────────────

def record_install(name: str, version: str, keg: Path):
    db = _load_db()
    pkg = db.setdefault(name, {"versions": {}, "linked": None})
    pkg["versions"][version] = {
        "keg": str(keg),
        "installed_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_db(db)


def record_link(name: str, version: str | None, linked_files: list[str] | None = None):
    """Set the linked version and the list of files linked into root (None = unlinked)."""
    db = _load_db()
    if name in db:
        db[name]["linked"] = version
        db[name]["linked_files"] = linked_files if version else []
        _save_db(db)


def record_uninstall(name: str, version: str | None = None):
    """Remove one version or the whole package entry."""
    db = _load_db()
    if name not in db:
        return
    if version is None:
        del db[name]
    else:
        db[name]["versions"].pop(version, None)
        if db[name]["linked"] == version:
            db[name]["linked"] = None
            db[name]["linked_files"] = []
        if not db[name]["versions"]:
            del db[name]
    _save_db(db)


# ── read ─────────────────────────────────────────────────────────────────────

def get_info(name: str) -> dict | None:
    return _load_db().get(name)


def list_installed() -> dict:
    return _load_db()


def is_installed(name: str, version: str | None = None) -> bool:
    db = _load_db()
    if name not in db:
        return False
    if version is None:
        return bool(db[name]["versions"])
    return version in db[name]["versions"]


def installed_versions(name: str) -> list[str]:
    return list(_load_db().get(name, {}).get("versions", {}).keys())


def linked_version(name: str) -> str | None:
    return _load_db().get(name, {}).get("linked")


def linked_files(name: str) -> list[str]:
    """Return the list of relative paths linked into root for the given package."""
    return _load_db().get(name, {}).get("linked_files") or []


def installed_version(name: str) -> str | None:
    """Alias for linked_version — kept for backwards compatibility."""
    return linked_version(name)
