from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from .config import config


class Formula:
    name: str = ""
    version: str = ""
    url: str = ""
    sha256: str = ""
    dependencies: list[str] = []

    # Override to use a different build system: "autoconf" | "cmake" | "meson" | "custom"
    build_system: str = "autoconf"

    # Extra args appended to the configure/cmake/meson step
    extra_configure_args: list[str] = []

    @property
    def keg(self) -> Path:
        return config.cellar / self.name / self.version

    def configure_args(self) -> list[str]:
        """Return the full argument list for the configure step."""
        base = [f"--prefix={self.keg}"]
        return base + self.extra_configure_args

    def cmake_args(self) -> list[str]:
        base = [f"-DCMAKE_INSTALL_PREFIX={self.keg}"]
        return base + self.extra_configure_args

    def meson_args(self) -> list[str]:
        base = [f"--prefix={self.keg}"]
        return base + self.extra_configure_args

    def post_install(self):
        """Hook called after installation. Override for custom post-install steps."""


def load_formula(name: str) -> Formula:
    """Load a Formula class by package name from the formulas directory."""
    formulas_dir = config.formulas_dir
    formula_file = formulas_dir / f"{name}.py"
    if not formula_file.exists():
        raise FileNotFoundError(f"No formula found for '{name}' (looked in {formulas_dir})")

    spec = importlib.util.spec_from_file_location(f"formulas.{name}", formula_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"formulas.{name}"] = module
    spec.loader.exec_module(module)

    # Find the Formula subclass defined in the module
    for attr in vars(module).values():
        if (
            isinstance(attr, type)
            and issubclass(attr, Formula)
            and attr is not Formula
        ):
            return attr()

    raise ValueError(f"Formula file '{formula_file}' contains no Formula subclass")


def list_available(formulas_dir: Path | None = None) -> list[str]:
    """Return names of all available formulas."""
    d = formulas_dir or config.formulas_dir
    return sorted(p.stem for p in d.glob("*.py") if p.stem != "__init__")
