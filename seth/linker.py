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


def link(formula: Formula, force: bool = False):
    keg = formula.keg
    if not keg.exists():
        raise FileNotFoundError(f"Keg not found: {keg}")

    root = config.root
    conflicts = []

    for keg_file, rel in _iter_keg_files(keg):
        target = root / rel
        if target.exists() and not target.is_symlink():
            conflicts.append(target)
        elif target.is_symlink() and not force:
            existing_target = target.resolve()
            if existing_target != keg_file.resolve():
                conflicts.append(target)

    if conflicts and not force:
        conflict_list = "\n  ".join(str(c) for c in conflicts)
        raise FileExistsError(
            f"Conflicts found (use --force to overwrite):\n  {conflict_list}"
        )

    linked = 0
    for keg_file, rel in _iter_keg_files(keg):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            target.unlink()
        target.symlink_to(keg_file)
        linked += 1

    from . import colors as col
    print(col.header(f"Linked {col.cyan(str(linked))} files into {col.dim(str(root))}"))


def unlink(formula: Formula):
    keg = formula.keg
    root = config.root
    removed = 0

    for keg_file, rel in _iter_keg_files(keg):
        target = root / rel
        if target.is_symlink() and target.resolve() == keg_file.resolve():
            target.unlink()
            removed += 1
            _rmdir_if_empty(target.parent, root)

    from . import colors as col
    print(col.header(f"Unlinked {col.cyan(str(removed))} files from {col.dim(str(root))}"))


def _rmdir_if_empty(directory: Path, stop_at: Path):
    """Remove empty directories up to (but not including) stop_at."""
    while directory != stop_at and directory.exists():
        try:
            directory.rmdir()
            directory = directory.parent
        except OSError:
            break
