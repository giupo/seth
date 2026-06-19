"""seth CLI entry point."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

from . import __version__
from . import cellar, colors as col, linker
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

def _filter_plan(plan: list[PlannedStep], force: bool, link: bool = True) -> list[PlannedStep]:
    """Return steps that still need work.

    A step is needed when:
    - force=True (always rebuild+relink), OR
    - the package is not installed (needs build+link), OR
    - the package is installed but the correct version is not linked in root
      (needs at least re-link; this happens e.g. after a failed link on a
      previous run, or after --no-link was used)

    When link=False (--no-link) the third condition is skipped because the
    caller does not intend to link anything.
    """
    return [
        step for step in plan
        if force
        or not cellar.is_installed(step.formula.name, step.formula.version)
        or (link and cellar.linked_version(step.formula.name) != step.formula.version)
    ]


def _print_plan(steps: list[PlannedStep], target_name: str):
    deps = [s for s in steps if s.formula.name != target_name]
    if deps:
        print(col.header("Dependencies:"))
        for s in deps:
            f = s.formula
            suffix = col.dim(col.yellow("  (build only)")) if s.build_only else ""
            print(f"    {col.pkg(f.name, f.version)}{suffix}")


def _execute_plan(steps: list[PlannedStep], link: bool, force: bool, debug: bool = False):
    config.ensure_dirs()
    for step in steps:
        f = step.formula
        # If the keg was already built (e.g. a previous run built it but then
        # failed during linking), skip the expensive build and go straight to
        # (re-)linking.
        already_built = (
            not force
            and cellar.is_installed(f.name, f.version)
            and f.keg.exists()
        )
        if not already_built:
            builder_install(f, debug=debug)
            cellar.record_install(f.name, f.version, f.keg)
        elif link:
            print(col.header(f"Relinking {col.pkg(f.name, f.version)}"))
        if link:
            linked_files = linker.link(f, force=force)
            cellar.record_link(f.name, f.version, linked_files)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_install(args):
    for spec in args.packages:
        name, version = _parse_pkg(spec)
        formula = load_formula(name, version)
        plan = build_install_plan(formula)
        link = not args.no_link
        steps = _filter_plan(plan, args.force, link=link)

        if not steps:
            print(
                f"seth: {col.pkg(formula.name, formula.version)} already installed"
                f" {col.dim('(use --force to reinstall)')}"
            )
            continue

        _print_plan(steps, formula.name)
        _execute_plan(steps, link=link, force=args.force, debug=args.debug)


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
                linker.unlink(cellar.linked_files(name))
                cellar.record_link(name, None)
            keg = config.cellar / name / ver
            if keg.exists():
                shutil.rmtree(keg)
                print(col.header(f"Removed {col.dim(str(keg))}"))
                try:
                    keg.parent.rmdir()
                except OSError:
                    pass
            cellar.record_uninstall(name, ver)


def cmd_list(args):
    installed = cellar.list_installed()
    if not installed:
        print(col.dim("No packages installed."))
        return
    for name, info in sorted(installed.items()):
        linked = info.get("linked")
        for ver in sorted(info["versions"], reverse=True):
            if ver == linked:
                marker = "  " + col.b_green("✓ linked")
            else:
                marker = ""
            print(f"  {col.pkg(name, ver)}{marker}")


def cmd_info(args):
    name, version = _parse_pkg(args.package)
    formula = load_formula(name, version)

    all_vers = available_versions(name)
    linked = cellar.linked_version(name)
    inst_vers = cellar.installed_versions(name)

    def field(label: str, value: str):
        # Pad the plain label first, then apply bold so ANSI codes don't skew width.
        padded = f"{label + ':':<14}"
        print(f"  {col.bold(padded)}  {value}")

    print(col.header(col.pkg(formula.name, formula.version)))
    field("Latest",       col.cyan(formula.latest or formula.version))
    field("Available",    "  ".join(col.cyan(v) for v in all_vers) if all_vers else col.cyan(formula.version))
    field("Build system", formula.build_system)
    if formula.dependencies:
        field("Dependencies", "  ".join(col.bold(d) for d in formula.dependencies))
    if formula.build_dependencies:
        field("Build deps",   "  ".join(col.dim(d) for d in formula.build_dependencies))
    if inst_vers:
        inst_str = "  ".join(
            (col.b_green(v + " ✓") if v == linked else col.cyan(v))
            for v in sorted(inst_vers, reverse=True)
        )
        field("Installed", inst_str)
    else:
        field("Installed", col.dim("no"))


def cmd_link(args):
    name, version = _parse_pkg(args.package)
    if not cellar.is_installed(name):
        print(f"seth: {name} is not installed")
        sys.exit(1)

    version = version or cellar.installed_versions(name)[-1]
    formula = load_formula(name, version)

    current = cellar.linked_version(name)
    if current and current != version:
        linker.unlink(cellar.linked_files(name))
        cellar.record_link(name, None)

    linked_files = linker.link(formula, force=args.force)
    cellar.record_link(name, formula.version, linked_files)


def cmd_unlink(args):
    name, version = _parse_pkg(args.package)
    linked = cellar.linked_version(name)
    if not linked:
        print(f"seth: {name} is not linked")
        sys.exit(1)
    files = cellar.linked_files(name)
    if not files:
        # Legacy entry: linked_files not recorded — rebuild list from keg.
        files = linker.scan_keg_files(config.cellar / name / linked)
    linker.unlink(files)
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

        arrow = col.cyan("→")
        print(col.header(
            f"Upgrading {col.bold(name)}: "
            f"{col.dim(current or '—')} {arrow} {col.cyan(formula.version)}"
        ))
        plan = build_install_plan(formula)
        steps = _filter_plan(plan, args.force, link=True)

        if current:
            linker.unlink(cellar.linked_files(name))
            cellar.record_link(name, None)

        _execute_plan(steps, link=True, force=True)


def cmd_update(args):
    do_update()


def cmd_edit(args):
    import subprocess
    import tempfile
    from .formula import _find_formula_file
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vi"
    try:
        path = _find_formula_file(args.formula)
        os.execvp(editor, [editor, str(path)])
    except FileNotFoundError:
        # New formula: open a temp file pre-filled with the template.
        # Only write to the real path if the user saves changes.
        template = _formula_template(args.formula)
        dest = _new_formula_path(args.formula)
        print(col.header(f"New formula: {col.dim(str(dest))}"))
        with tempfile.NamedTemporaryFile(
            suffix=".py", prefix=f"seth.{args.formula}.", mode="w", delete=False
        ) as tmp:
            tmp.write(template)
            tmp_path = Path(tmp.name)
        try:
            subprocess.run([editor, str(tmp_path)], check=False)
            content = tmp_path.read_text()
            if content != template:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content)
                print(col.header(f"Saved {col.dim(str(dest))}"))
            else:
                print(col.dim("(no changes — formula not saved)"))
        finally:
            tmp_path.unlink(missing_ok=True)


def _new_formula_path(name: str) -> Path:
    # Write new formulas to the last search dir (bundled/local), not the remote cache.
    return config.formula_search_dirs[-1] / f"{name}.py"


def _formula_template(name: str) -> str:
    class_name = "".join(part.capitalize() for part in name.replace("-", "_").split("_"))
    return f'''\
from seth.formula import Formula
from seth.types import BuildType

class {class_name}Formula(Formula):
    name = "{name}"
    latest = "0.0.0"

    # dependencies = []
    # build_dependencies = []
    # build_system = BuildType.AUTOCONF
    
    versions = {{
        "0.0.0": {{
            "url": "https://example.com/{name}-0.0.0.tar.gz",
            "sha256": "",
        }},
    }}

    # def configure_args(self):
    #     return [
    #         f"--prefix={{self.keg}}",
    #         "--enable-shared",
    #     ]

    # def configure_args(self) -> list[str]:
    #    return [f"--prefix={{self.keg}}"] + self.extra_configure_args

    # def make_args(self) -> list[str]:
    #    """Variables/flags appended to every `make` invocation (e.g. CFLAGS=-O2)."""
    #     return self.extra_make_args

    # def cmake_args(self) -> list[str]:
    #    return [f"-DCMAKE_INSTALL_PREFIX={{self.keg}}"] + self.extra_configure_args

    # def meson_args(self) -> list[str]:
    #    return [f"--prefix={{self.keg}}"] + self.extra_configure_args

    # def patch(self, source_dir: Path):
    #     """Override for programmatic source modifications applied before build."""

    # def post_install(self):
    #     pass

'''


def cmd_init(args):
    import configparser

    config_path = Path(
        os.environ.get(
            "SETH_CONFIG",
            Path.home() / ".config" / "seth" / "seth.conf"
        )
    )

    def _ask_path(label: str, default: Path) -> Path:
        padded = f"{label}:"
        prompt = f"  {col.bold(f'{padded:<22}')} [{col.cyan(str(default))}] "
        try:
            val = input(prompt).strip()
        except EOFError:
            val = ""
        return Path(val).expanduser() if val else default

    def _ask_str(label: str, default: str) -> str:
        padded = f"{label}:"
        hint = col.cyan(default) if default else col.dim("(leave empty to skip)")
        prompt = f"  {col.bold(f'{padded:<22}')} [{hint}] "
        try:
            val = input(prompt).strip()
        except EOFError:
            val = ""
        return val if val else default

    if config_path.exists() and not args.force:
        print(col.header("seth is already configured"))
        print(f"  {col.dim(str(config_path))}")
        print()
        try:
            answer = input(f"  Overwrite? [{col.yellow('y/N')}] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print(col.dim("  Cancelled."))
            return
        print()

    print(col.header("seth initialization"))
    print(col.dim(f"  Config file: {config_path}"))
    print(col.dim("  Press Enter to accept the default shown in [brackets]."))
    print()

    default_root = Path.home() / ".local" / "seth"
    root = _ask_path("Root prefix", default_root)
    cellar = _ask_path("Cellar", root / "Cellar")
    formulas_url = _ask_str("Remote formulas URL", "")
    tmp_dir = _ask_str("Temp dir", None)
    
    print()

    cfg = configparser.ConfigParser()
    cfg["paths"] = {
        "root": str(root)
    }
    
    if cellar != root / "Cellar":
        cfg["paths"]["cellar"] = str(cellar)

    if formulas_url:
        cfg["formulas"] = {"url": formulas_url}

    if tmp_dir:
        cfg["paths"]["tmp_dir"] = str(tmp_dir)
        
        
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        cfg.write(f)

    for d in (root, cellar, root / "bin", root / "lib", root / "include"):
        d.mkdir(parents=True, exist_ok=True)

    print(col.header(f"Written {col.dim(str(config_path))}"))

    def field(label: str, value: str):
        padded = f"{label + ':':<14}"
        print(f"  {col.bold(padded)}  {value}")

    field("root",   col.cyan(str(root)))
    field("cellar", col.dim(str(cellar)))
    if formulas_url:
        field("formulas", col.cyan(formulas_url))

    if formulas_url:
        print()
        try:
            answer = input(f"  Download formulas now? [{col.cyan('Y/n')}] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("n", "no"):
            from .updater import update as do_update
            config.__init__()   # re-read the file we just wrote
            do_update()

    print()
    print(col.dim("  Add seth to your shell environment:"))
    print(col.dim('    eval "$(seth env)"'))


def cmd_search(args):
    term = args.term.lower()
    matches = [n for n in list_available() if term in n]
    if not matches:
        print(col.dim(f"No formulas matching '{args.term}'"))
        return
    for m in matches:
        inst = cellar.linked_version(m)
        marker = f"  {col.b_green('✓ ' + inst)}" if inst else ""
        print(f"  {col.bold(m)}{marker}")


def cmd_available(args):
    for name in list_available():
        inst = cellar.linked_version(name)
        marker = f"  {col.b_green('✓ ' + inst)}" if inst else ""
        print(f"  {col.bold(name)}{marker}")


def cmd_config(args):
    def field(label: str, value: str):
        padded = f"{label + ':':<14}"
        print(f"  {col.bold(padded)}  {value}")

    print(col.header("seth configuration"))
    field("root",         col.cyan(str(config.root)))
    field("cellar",       col.dim(str(config.cellar)))
    field("formulas_url", col.cyan(config.formulas_url) if config.formulas_url
                          else col.dim("(not configured)"))
    field("db",           col.dim(str(config.db_path)))
    print(f"  {col.bold('formulas:')}")
    for d in config.formula_search_dirs:
        suffix = f"  {col.dim('[remote cache]')}" if d == config.remote_formulas_dir else ""
        print(f"    {col.dim(str(d))}{suffix}")


def cmd_purge(args):
    print(f"  {col.bold('Delete downloads')}")
    for item in config.downloads.iterdir():
        if item.is_file():
            item.unlink()


        
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
                             root / "lib64" / "pkgconfig",
                             root / "share" / "pkgconfig"]),
        ("MANPATH",         [root / "share" / "man"]),
        ("ACLOCAL_PATH",    [root / "share" / "aclocal"]),
    ]

    print(col.dim(f"# seth environment — root: {root}"))
    print(col.dim('# To apply: eval "$(seth env)"'))
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

    p = sub.add_parser("init", help="Interactive first-time setup: write config and create directories")
    p.add_argument("--force", action="store_true", help="Overwrite existing config without prompting")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("config", help="Show current configuration")
    p.set_defaults(func=cmd_config)

    p = sub.add_parser("env", help="Print shell environment variables for the seth root prefix")
    p.set_defaults(func=cmd_env)

    p = sub.add_parser("edit", help="Open a formula in $EDITOR")
    p.add_argument("formula", metavar="formula")
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("purge", help="Remove all downloaded tarballs")
    p.set_defaults(func=cmd_purge)

    args = parser.parse_args()
    try:
        args.func(args)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as e:
        print(f"{col.b_red('seth: error:')} {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{col.yellow('seth: interrupted')}", file=sys.stderr)
        sys.exit(130)
