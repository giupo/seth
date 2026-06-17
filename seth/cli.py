"""seth CLI entry point."""

from __future__ import annotations

import argparse
import os
import shutil
import sys

from . import __version__
from . import cellar, linker
from .builder import install as builder_install
from .config import config
from .formula import available_versions, list_available, load_formula
from .resolver import PlannedStep, build_install_plan
from .updater import update as do_update


def _parse_pkg(spec: str) -> tuple[str, str | None]:
    """Split 'pkg@version' → (name, version). Version is None if absent."""
    name, _, ver = spec.partition("@")
    return name, ver or None


# ── install helpers ───────────────────────────────────────────────────────────

def _filter_plan(plan: list[PlannedStep], force: bool) -> list[PlannedStep]:
    """Return only the steps that actually need to run."""
    return [
        step for step in plan
        if force or not cellar.is_installed(step.formula.name, step.formula.version)
    ]


def _print_plan(steps: list[PlannedStep], target_name: str):
    deps = [s for s in steps if s.formula.name != target_name]
    if deps:
        print(f"==> Dependencies:")
        for s in deps:
            print(f"    {s}")


def _execute_plan(steps: list[PlannedStep], link: bool, force: bool, debug: bool = False):
    config.ensure_dirs()
    for step in steps:
        builder_install(step.formula, debug=debug)
        cellar.record_install(step.formula.name, step.formula.version, step.formula.keg)
        if link:
            linker.link(step.formula, force=force)
            cellar.record_link(step.formula.name, step.formula.version)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_install(args):
    for spec in args.packages:
        name, version = _parse_pkg(spec)
        formula = load_formula(name, version)
        plan = build_install_plan(formula)
        steps = _filter_plan(plan, args.force)

        if not steps:
            print(f"seth: {formula.name} {formula.version} already installed"
                  f" (use --force to reinstall)")
            continue

        _print_plan(steps, formula.name)
        _execute_plan(steps, link=not args.no_link, force=args.force, debug=args.debug)


def cmd_uninstall(args):
    for spec in args.packages:
        name, version = _parse_pkg(spec)
        info = cellar.get_info(name)

        if not info:
            print(f"seth: {name} is not installed")
            continue

        targets = (
            [version] if version and cellar.is_installed(name, version)
            else list(info["versions"].keys()) if not version
            else []
        )
        if not targets:
            print(f"seth: {name} {version} is not installed")
            continue

        for ver in targets:
            if info.get("linked") == ver:
                linker.unlink(load_formula(name, ver))
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
        for ver in sorted(info["versions"], reverse=True):
            marker = " (linked)" if ver == linked else ""
            print(f"  {name} {ver}{marker}")


def cmd_info(args):
    name, version = _parse_pkg(args.package)
    formula = load_formula(name, version)
    info = cellar.get_info(name)

    all_vers = available_versions(name)
    linked = cellar.linked_version(name)
    inst_vers = cellar.installed_versions(name)

    print(f"Name:          {formula.name}")
    print(f"Latest:        {formula.latest or formula.version}")
    print(f"Available:     {', '.join(all_vers) if all_vers else formula.version}")
    print(f"Build system:  {formula.build_system}")
    if formula.dependencies:
        print(f"Dependencies:  {', '.join(formula.dependencies)}")
    if formula.build_dependencies:
        print(f"Build deps:    {', '.join(formula.build_dependencies)}")
    if inst_vers:
        print(f"Installed:     {', '.join(sorted(inst_vers, reverse=True))}")
        print(f"Linked:        {linked or 'none'}")
    else:
        print("Installed:     no")


def cmd_link(args):
    name, version = _parse_pkg(args.package)
    if not cellar.is_installed(name):
        print(f"seth: {name} is not installed")
        sys.exit(1)

    version = version or cellar.installed_versions(name)[-1]
    formula = load_formula(name, version)

    current = cellar.linked_version(name)
    if current and current != version:
        linker.unlink(load_formula(name, current))

    linker.link(formula, force=args.force)
    cellar.record_link(name, formula.version)


def cmd_unlink(args):
    name, version = _parse_pkg(args.package)
    linked = cellar.linked_version(name)
    if not linked:
        print(f"seth: {name} is not linked")
        sys.exit(1)
    linker.unlink(load_formula(name, version or linked))
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
        plan = build_install_plan(formula)
        steps = _filter_plan(plan, args.force)

        if current:
            linker.unlink(load_formula(name, current))

        _execute_plan(steps, link=True, force=True)


def cmd_update(args):
    do_update()


def cmd_edit(args):
    from .formula import _find_formula_file
    path = _find_formula_file(args.formula)
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vi"
    os.execvp(editor, [editor, str(path)])


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


def cmd_env(args):
    root = config.root

    # Ordered list of (env_var, [dirs_to_prepend])
    # PATH and LD_LIBRARY_PATH first, then build/compile helpers.
    entries = [
        ("PATH",            [root / "bin", root / "sbin"]),
        ("LD_LIBRARY_PATH", [root / "lib", root / "lib64"]),
        ("LIBRARY_PATH",    [root / "lib", root / "lib64"]),
        ("CPATH",           [root / "include"]),
        ("PKG_CONFIG_PATH", [root / "lib" / "pkgconfig",
                             root / "share" / "pkgconfig"]),
        ("MANPATH",         [root / "share" / "man"]),
        ("ACLOCAL_PATH",    [root / "share" / "aclocal"]),
    ]

    print(f"# seth environment — root: {root}")
    print(f'# To apply: eval "$(seth env)"')
    print()
    for var, dirs in entries:
        paths = ":".join(str(d) for d in dirs)
        # ${VAR:+:${VAR}} expands to :$VAR when VAR is set/non-empty, else ""
        # This avoids a trailing/leading colon when the original var is unset.
        print(f'export {var}="{paths}${{{var}:+:${{{var}}}}}"')


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
    p.add_argument("--debug", action="store_true",
                   help="Preserve build directory after install for inspection")
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

    p = sub.add_parser("upgrade", help="Upgrade installed packages")
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

    p = sub.add_parser("env", help="Print shell environment variables for the seth root prefix")
    p.set_defaults(func=cmd_env)

    p = sub.add_parser("edit", help="Open a formula in $EDITOR")
    p.add_argument("formula", metavar="formula")
    p.set_defaults(func=cmd_edit)

    args = parser.parse_args()
    try:
        args.func(args)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as e:
        print(f"seth: error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nseth: interrupted", file=sys.stderr)
        sys.exit(130)
