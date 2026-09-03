"""Symlink a keg's contents into the root prefix."""

from __future__ import annotations

from pathlib import Path

from .config import config
from .formula import Formula

# Files that must not be symlinked because they are shared aggregate indexes
# written by multiple packages (e.g. install-info writes share/info/dir for
# every package that ships texinfo pages — it cannot be a per-keg symlink).
_SKIP_LINK = frozenset([
    "share/info/dir",
])


def _iter_keg_files(keg: Path):
    """Yield (keg_file, relative_path) for every non-aggregate file in the keg."""
    for f in keg.rglob("*"):
        if f.is_file() or f.is_symlink():
            rel = f.relative_to(keg)
            if str(rel) not in _SKIP_LINK:
                yield f, rel


def link(formula: Formula, force: bool = False) -> list[str]:
    """Symlink keg into root. Returns list of relative paths that were linked.

    A target already occupied by something this keg doesn't own (a real file,
    or a symlink into a different keg — typically another package that bundles
    the same library) is left untouched and reported, instead of being
    overwritten: it's not this install's file to take, and skipping it means
    it's never recorded as one of *this* package's linked_files, so a later
    `seth uninstall` can't remove a symlink another package still depends on.
    --force overrides this and relinks everything into this keg regardless.
    """
    keg = formula.keg
    if not keg.exists():
        raise FileNotFoundError(f"Keg not found: {keg}")

    root = config.root
    linked_files: list[str] = []
    skipped: list[Path] = []

    for keg_file, rel in _iter_keg_files(keg):
        target = root / rel
        is_symlink = target.is_symlink()
        already_ours = is_symlink and target.readlink() == keg_file
        conflict = not already_ours and (target.exists() or is_symlink)

        if conflict and not force:
            skipped.append(target)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        if is_symlink or target.exists():
            target.unlink()
        target.symlink_to(keg_file)
        linked_files.append(str(rel))

    from . import colors as col
    if skipped:
        skip_list = "\n  ".join(str(s) for s in skipped)
        print(col.header(
            f"{col.yellow('Skipped')} {col.cyan(str(len(skipped)))} file(s) "
            f"already provided by another linked package (use --force to overwrite):\n  {skip_list}"
        ))
    print(col.header(f"Linked {col.cyan(str(len(linked_files)))} files into {col.dim(str(root))}"))
    return linked_files


def unlink(root_files: list[str]):
    """Remove symlinks from root given the list of relative paths recorded at link time."""
    root = config.root
    removed = 0

    for rel in root_files:
        target = root / rel
        if target.is_symlink():
            target.unlink()
            removed += 1
            _rmdir_if_empty(target.parent, root)

    from . import colors as col
    print(col.header(f"Unlinked {col.cyan(str(removed))} files from {col.dim(str(root))}"))


def scan_keg_files(keg: Path) -> list[str]:
    """Return relative paths of all linkable files in a keg (used as legacy fallback)."""
    if not keg.exists():
        return []
    return [str(rel) for _, rel in _iter_keg_files(keg)]


def _rmdir_if_empty(directory: Path, stop_at: Path):
    """Remove empty directories up to (but not including) stop_at."""
    while directory != stop_at and directory.exists():
        try:
            directory.rmdir()
            directory = directory.parent
        except OSError:
            break
