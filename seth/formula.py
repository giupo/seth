"""Formula base class and dynamic loader.

A formula file defines a class that inherits from Formula.
Multiple versions are declared in the `versions` dict:

    class WgetFormula(Formula):
        name = "wget"
        latest = "1.21.4"
        dependencies = ["openssl"]

        versions = {
            "1.21.4": {"url": "...", "sha256": "..."},
            "1.21.3": {"url": "...", "sha256": "..."},
            # version-level overrides: any callable or attribute is also accepted
            "1.20.0": {"url": "...", "sha256": "...",
                       "configure_args": lambda self: [f"--prefix={self.keg}"]},
        }

        def configure_args(self):   # default for all versions
            return [f"--prefix={self.keg}", "--with-ssl=openssl"]

load_formula("wget")          → latest version
load_formula("wget", "1.21.3") → specific version
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from .config import config


class Formula:
    name: str = ""
    latest: str = ""
    dependencies: list[str] = []
    build_dependencies: list[str] = []   # needed only at build time, not at runtime
    build_system: str = "autoconf"
    extra_configure_args: list[str] = []
    versions: dict = {}
    # Ordered list of .patch filenames (unified diff, applied with patch -p1).
    # Files are searched in patch_dirs/<formula_name>/ (see config).
    patches: list[str] = []

    # Populated per-instance by load_formula
    version: str = ""
    url: str = ""
    sha256: str = ""

    @property
    def keg(self) -> Path:
        return config.cellar / self.name / self.version

    def configure_args(self) -> list[str]:
        return [f"--prefix={self.keg}"] + self.extra_configure_args

    def cmake_args(self) -> list[str]:
        return [f"-DCMAKE_INSTALL_PREFIX={self.keg}"] + self.extra_configure_args

    def meson_args(self) -> list[str]:
        return [f"--prefix={self.keg}"] + self.extra_configure_args

    def patch(self, source_dir: Path):
        """Override for programmatic source modifications applied before build."""

    def post_install(self):
        pass


# ── internal helpers ──────────────────────────────────────────────────────────

def _find_formula_file(name: str) -> Path:
    for d in config.formula_search_dirs:
        p = d / f"{name}.py"
        if p.exists():
            return p
    searched = " → ".join(str(d) for d in config.formula_search_dirs)
    raise FileNotFoundError(f"No formula found for '{name}' (searched: {searched})")


def _load_module(name: str, path: Path):
    key = f"_seth_formula_{name}"
    sys.modules.pop(key, None)          # always reload so edits are picked up
    spec = importlib.util.spec_from_file_location(key, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


def _find_base_class(module) -> type[Formula]:
    for attr in vars(module).values():
        if isinstance(attr, type) and issubclass(attr, Formula) and attr is not Formula:
            return attr
    raise ValueError(f"No Formula subclass found in {module.__file__}")


# ── public API ────────────────────────────────────────────────────────────────

def load_formula(name: str, version: str | None = None) -> Formula:
    """Load and instantiate a formula for the given package and version."""
    path = _find_formula_file(name)
    module = _load_module(name, path)
    base_cls = _find_base_class(module)

    versions_dict = getattr(base_cls, "versions", {})

    if not versions_dict:
        # Legacy single-version formula: version/url/sha256 are class attributes.
        return base_cls()

    target = version or getattr(base_cls, "latest", "")
    if not target:
        raise ValueError(f"No version specified and no 'latest' defined for '{name}'")

    if target not in versions_dict:
        available = ", ".join(sorted(versions_dict, reverse=True))
        raise ValueError(
            f"Version '{target}' not available for '{name}'. Available: {available}"
        )

    entry = dict(versions_dict[target])
    url = entry.pop("url", "")
    sha256 = entry.pop("sha256", "")
    # Remaining keys are attribute/method overrides (e.g. configure_args lambda).
    attrs = {"version": target, "url": url, "sha256": sha256, **entry}

    dynamic_cls = type(
        f"{base_cls.__name__}_{target.replace('.', '_').replace('-', '_')}",
        (base_cls,),
        attrs,
    )
    return dynamic_cls()


def available_versions(name: str) -> list[str]:
    """Return all declared versions for a package, newest first."""
    path = _find_formula_file(name)
    module = _load_module(name, path)
    base_cls = _find_base_class(module)
    return sorted(base_cls.versions.keys(), reverse=True)


def _find_patch_file(formula_name: str, patch_file: str) -> Path:
    for d in config.patch_dirs:
        p = d / formula_name / patch_file
        if p.exists():
            return p
    searched = " → ".join(str(d / formula_name) for d in config.patch_dirs)
    raise FileNotFoundError(
        f"Patch '{patch_file}' not found for '{formula_name}' (searched: {searched})"
    )


def list_available() -> list[str]:
    """Return names of all available formulas (remote then bundled, deduped)."""
    seen: set[str] = set()
    names: list[str] = []
    for d in config.formula_search_dirs:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.py")):
            if p.stem != "__init__" and p.stem not in seen:
                seen.add(p.stem)
                names.append(p.stem)
    return names
