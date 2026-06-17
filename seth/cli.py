"""seth CLI entry point."""

from __future__ import annotations

import argparse
import shutil
import sys

from . import __version__
from . import cellar, linker
from .builder import install as builder_install
from .config import config
from .formula import Formula, available_versions, list_available, load_formula
from .updater import update as do_update


def _parse_pkg(spec: str) -> tuple[str, str | None]:
    """Split 'pkg@version' into (name, version). Version is None if absent."""
    name, _, ver = spec.partition("@")
    return name, ver or None


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_install(args):
    for spec in args.packages:
        name, version = _parse_pkg(spec)
        formula = load_formula(name, version)

        if cellar.is_installed(name, formula.version) and not args.force:
            print(f"seth: {name} {formula.version} already installed (use --force to reinstall)")
            continue

        _install_deps(formula)
        config.ensure_dirs()
        builder_install(formula)
        cellar.record_install(name, formula.version, formula.keg)

        if not args.no_link:
            linker.link(formula, force=args.force)
            cellar.record_link(name, formula.version)


def _install_deps(formula: Formula):
    for dep in formula.dependencies:
        if not cellar.is_installed(dep):
            print(f"==> Dependency: {dep}")
            dep_formula = load_formula(dep)
            _install_deps(dep_formula)
            config.ensure_dirs()
            builder_install(dep_formula)
            cellar.record_install(dep, dep_formula.version, dep_formula.keg)
            linker.link(dep_formula)
            cellar.record_link(dep, dep_formula.version)


def cmd_uninstall(args):
    for spec in args.packages:
        name, version = _parse_pkg(spec)
        info = cellar.get_info(name)

        if not info:
            print(f"seth: {name} is not installed")
            continue

        # Determine which version(s) to remove
        if version:
            targets = [version] if cellar.is_installed(name, version) else []
            if not targets:
                print(f"seth: {name} {version} is not installed")
                continue
        else:
            targets = list(info["versions"].keys())

        for ver in targets:
            if info.get("linked") == ver:
                formula = load_formula(name, ver)
                linker.unlink(formula)
            keg = config.cellar / name / ver
            if keg.exists():
                shutil.rmtree(keg)
                print(f"==> Removed {keg}")
                try:
                    keg.parent.rmdir()
                except OSError:
                    pass
            cellar.record_uninstall(name, ver)


def cmd_list(args):
    installed = cellar.list_installed()
    if not installed:
        print("No packages installed.")
        return
    for name, info in sorted(installed.items()):
        linked = info.get("linked")
        vers = sorted(info["versions"].keys(), reverse=True)
        for ver in vers:
            marker = " (linked)" if ver == linked else ""
            print(f"  {name} {ver}{marker}")


def cmd_info(args):
    name, version = _parse_pkg(args.package)
    formula = load_formula(name, version)
    info = cellar.get_info(name)

    all_versions = available_versions(name)
    linked = cellar.linked_version(name)
    inst_vers = cellar.installed_versions(name)

    print(f"Name:         {formula.name}")
    print(f"Latest:       {formula.latest or formula.version}")
    print(f"Available:    {', '.join(all_versions) if all_versions else formula.version}")
    print(f"Build system: {formula.build_system}")
    print(f"Dependencies: {', '.join(formula.dependencies) or 'none'}")
    if inst_vers:
        print(f"Installed:    {', '.join(sorted(inst_vers, reverse=True))}")
        print(f"Linked:       {linked or 'none'}")
    else:
        print("Installed:    no")


def cmd_link(args):
    name, version = _parse_pkg(args.package)
    if not cellar.is_installed(name):
        print(f"seth: {name} is not installed")
        sys.exit(1)
    version = version or cellar.linked_version(name) or cellar.installed_versions(name)[-1]
    formula = load_formula(name, version)

    # Unlink currently linked version first
    current_linked = cellar.linked_version(name)
    if current_linked and current_linked != version:
        linker.unlink(load_formula(name, current_linked))

    linker.link(formula, force=args.force)
    cellar.record_link(name, formula.version)


def cmd_unlink(args):
    name, version = _parse_pkg(args.package)
    linked = cellar.linked_version(name)
    if not linked:
        print(f"seth: {name} is not linked")
        sys.exit(1)
    formula = load_formula(name, version or linked)
    linker.unlink(formula)
    cellar.record_link(name, None)


def cmd_upgrade(args):
    for spec in args.packages:
        name, requested_version = _parse_pkg(spec)

        if not cellar.is_installed(name):
            print(f"seth: {name} is not installed, installing instead")

        formula = load_formula(name, requested_version)
        current = cellar.linked_version(name)

        if current == formula.version and not args.force:
            print(f"seth: {name} {formula.version} already up-to-date")
            continue

        print(f"==> Upgrading {name}: {current or '—'} → {formula.version}")

        if current:
            linker.unlink(load_formula(name, current))

        config.ensure_dirs()
        builder_install(formula)
        cellar.record_install(name, formula.version, formula.keg)
        linker.link(formula, force=True)
        cellar.record_link(name, formula.version)


def cmd_update(args):
    do_update()


def cmd_search(args):
    term = args.term.lower()
    matches = [n for n in list_available() if term in n]
    if not matches:
        print(f"No formulas matching '{args.term}'")
        return
    for m in matches:
        inst = cellar.linked_version(m)
        marker = f" [installed: {inst}]" if inst else ""
        print(f"  {m}{marker}")


def cmd_available(args):
    for name in list_available():
        inst = cellar.linked_version(name)
        marker = f" [installed: {inst}]" if inst else ""
        print(f"  {name}{marker}")


def cmd_config(args):
    print(f"root:          {config.root}")
    print(f"cellar:        {config.cellar}")
    print(f"formulas (search order):")
    for d in config.formula_search_dirs:
        tag = " [remote cache]" if d == config.remote_formulas_dir else ""
        print(f"               {d}{tag}")
    print(f"formulas_url:  {config.formulas_url or '(not configured)'}")
    print(f"db:            {config.db_path}")


# ── parser ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="seth",
        description="seth — source-based package manager for the Osiride platform",
    )
    parser.add_argument("--version", action="version", version=f"seth {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    p = sub.add_parser("install", help="Download, build and install packages")
    p.add_argument("packages", nargs="+", metavar="pkg[@version]")
    p.add_argument("--force", action="store_true", help="Reinstall even if already installed")
    p.add_argument("--no-link", action="store_true", help="Install into cellar without linking")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("uninstall", aliases=["remove", "rm"], help="Uninstall packages")
    p.add_argument("packages", nargs="+", metavar="pkg[@version]")
    p.set_defaults(func=cmd_uninstall)

    p = sub.add_parser("list", aliases=["ls"], help="List installed packages")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("info", help="Show information about a package")
    p.add_argument("package", metavar="pkg[@version]")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("link", help="Symlink a keg into the root prefix")
    p.add_argument("package", metavar="pkg[@version]")
    p.add_argument("--force", action="store_true", help="Overwrite existing symlinks")
    p.set_defaults(func=cmd_link)

    p = sub.add_parser("unlink", help="Remove symlinks from the root prefix")
    p.add_argument("package", metavar="pkg[@version]")
    p.set_defaults(func=cmd_unlink)

    p = sub.add_parser("upgrade", help="Upgrade installed packages to the latest formula version")
    p.add_argument("packages", nargs="+", metavar="pkg[@version]")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_upgrade)

    p = sub.add_parser("update", help="Fetch the remote formula repository")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("search", help="Search available formulas by name")
    p.add_argument("term", metavar="term")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("available", help="List all available formulas")
    p.set_defaults(func=cmd_available)

    p = sub.add_parser("config", help="Show current configuration")
    p.set_defaults(func=cmd_config)

    args = parser.parse_args()
    try:
        args.func(args)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as e:
        print(f"seth: error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nseth: interrupted", file=sys.stderr)
        sys.exit(130)
