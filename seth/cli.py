"""seth CLI entry point."""

from __future__ import annotations

import argparse
import shutil
import sys

from . import __version__
from . import cellar, linker
from .builder import install as builder_install
from .config import config
from .formula import Formula, list_available, load_formula


def cmd_install(args):
    for name in args.packages:
        if cellar.is_installed(name) and not args.force:
            current = cellar.installed_version(name)
            print(f"seth: {name} {current} already installed (use --force to reinstall)")
            continue
        formula = load_formula(name)
        _install_deps(formula)
        config.ensure_dirs()
        builder_install(formula)
        cellar.record_install(name, formula.version, formula.keg)
        if not args.no_link:
            linker.link(formula, force=args.force)
            cellar.record_link(name, True)


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
            cellar.record_link(dep, True)


def cmd_uninstall(args):
    for name in args.packages:
        info = cellar.get_info(name)
        if not info:
            print(f"seth: {name} is not installed")
            continue
        formula = load_formula(name)
        if info.get("linked"):
            linker.unlink(formula)
        keg = formula.keg
        if keg.exists():
            shutil.rmtree(keg)
            print(f"==> Removed {keg}")
            # Remove version dir parent if empty
            try:
                keg.parent.rmdir()
            except OSError:
                pass
        cellar.record_uninstall(name)


def cmd_list(args):
    installed = cellar.list_installed()
    if not installed:
        print("No packages installed.")
        return
    for name, info in sorted(installed.items()):
        linked = " (linked)" if info.get("linked") else ""
        print(f"  {name} {info['version']}{linked}")


def cmd_info(args):
    formula = load_formula(args.package)
    info = cellar.get_info(args.package)
    print(f"Name:         {formula.name}")
    print(f"Version:      {formula.version}")
    print(f"URL:          {formula.url}")
    print(f"Build system: {formula.build_system}")
    print(f"Dependencies: {', '.join(formula.dependencies) or 'none'}")
    print(f"Keg:          {formula.keg}")
    if info:
        print(f"Installed:    yes (at {info['installed_at']})")
        print(f"Linked:       {'yes' if info.get('linked') else 'no'}")
    else:
        print("Installed:    no")


def cmd_link(args):
    formula = load_formula(args.package)
    if not cellar.is_installed(args.package):
        print(f"seth: {args.package} is not installed")
        sys.exit(1)
    linker.link(formula, force=args.force)
    cellar.record_link(args.package, True)


def cmd_unlink(args):
    formula = load_formula(args.package)
    if not cellar.is_installed(args.package):
        print(f"seth: {args.package} is not installed")
        sys.exit(1)
    linker.unlink(formula)
    cellar.record_link(args.package, False)


def cmd_upgrade(args):
    for name in args.packages:
        if not cellar.is_installed(name):
            print(f"seth: {name} is not installed, installing instead")
        formula = load_formula(name)
        current = cellar.installed_version(name)
        if current == formula.version and not args.force:
            print(f"seth: {name} {formula.version} already up-to-date")
            continue
        print(f"==> Upgrading {name}: {current} → {formula.version}")
        old_formula_keg = formula.keg  # same object, keg derived from version
        if cellar.get_info(name) and cellar.get_info(name).get("linked"):
            linker.unlink(formula)
        config.ensure_dirs()
        builder_install(formula)
        cellar.record_install(name, formula.version, formula.keg)
        linker.link(formula, force=True)
        cellar.record_link(name, True)


def cmd_search(args):
    available = list_available()
    term = args.term.lower()
    matches = [n for n in available if term in n]
    if matches:
        for m in matches:
            installed_mark = " [installed]" if cellar.is_installed(m) else ""
            print(f"  {m}{installed_mark}")
    else:
        print(f"No formulas matching '{args.term}'")


def cmd_available(args):
    for name in list_available():
        installed_mark = " [installed]" if cellar.is_installed(name) else ""
        print(f"  {name}{installed_mark}")


def cmd_config(args):
    print(f"root:     {config.root}")
    print(f"cellar:   {config.cellar}")
    print(f"formulas: {config.formulas_dir}")
    print(f"db:       {config.db_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="seth",
        description="seth — source-based package manager for the Osiride platform",
    )
    parser.add_argument("--version", action="version", version=f"seth {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # install
    p = sub.add_parser("install", help="Download, build and install packages")
    p.add_argument("packages", nargs="+", metavar="package")
    p.add_argument("--force", action="store_true", help="Reinstall even if already installed")
    p.add_argument("--no-link", action="store_true", help="Install into cellar but do not link")
    p.set_defaults(func=cmd_install)

    # uninstall
    p = sub.add_parser("uninstall", aliases=["remove", "rm"], help="Uninstall packages")
    p.add_argument("packages", nargs="+", metavar="package")
    p.set_defaults(func=cmd_uninstall)

    # list
    p = sub.add_parser("list", aliases=["ls"], help="List installed packages")
    p.set_defaults(func=cmd_list)

    # info
    p = sub.add_parser("info", help="Show information about a package")
    p.add_argument("package", metavar="package")
    p.set_defaults(func=cmd_info)

    # link
    p = sub.add_parser("link", help="Symlink a package into the root prefix")
    p.add_argument("package", metavar="package")
    p.add_argument("--force", action="store_true", help="Overwrite existing symlinks")
    p.set_defaults(func=cmd_link)

    # unlink
    p = sub.add_parser("unlink", help="Remove symlinks for a package from the root prefix")
    p.add_argument("package", metavar="package")
    p.set_defaults(func=cmd_unlink)

    # upgrade
    p = sub.add_parser("upgrade", help="Upgrade installed packages")
    p.add_argument("packages", nargs="+", metavar="package")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_upgrade)

    # search
    p = sub.add_parser("search", help="Search available formulas")
    p.add_argument("term", metavar="term")
    p.set_defaults(func=cmd_search)

    # available
    p = sub.add_parser("available", help="List all available formulas")
    p.set_defaults(func=cmd_available)

    # config
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
