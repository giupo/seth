"""ANSI color helpers.

Colors are disabled automatically when:
  - stdout is not a TTY (pipe, redirect)
  - the NO_COLOR environment variable is set (https://no-color.org/)
"""

from __future__ import annotations

import os
import sys

ENABLED = not os.environ.get("NO_COLOR") and sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if ENABLED else text


# ── base styles ───────────────────────────────────────────────────────────────

def bold(t: str) -> str:    return _c("1",    t)
def dim(t: str) -> str:     return _c("2",    t)
def green(t: str) -> str:   return _c("32",   t)
def yellow(t: str) -> str:  return _c("33",   t)
def blue(t: str) -> str:    return _c("34",   t)
def magenta(t: str) -> str: return _c("35",   t)
def cyan(t: str) -> str:    return _c("36",   t)
def red(t: str) -> str:     return _c("31",   t)

def b_green(t: str) -> str: return _c("1;32", t)
def b_blue(t: str) -> str:  return _c("1;34", t)
def b_red(t: str) -> str:   return _c("1;31", t)
def b_cyan(t: str) -> str:  return _c("1;36", t)


# ── semantic helpers ──────────────────────────────────────────────────────────

def header(text: str) -> str:
    """==> Section header (bold blue arrow + bold text)."""
    return b_blue("==>") + " " + bold(text)


def pkg(name: str, version: str = "") -> str:
    """Bold package name with optional cyan version."""
    s = bold(name)
    if version:
        s += " " + cyan(version)
    return s


# ── step tags  ────────────────────────────────────────────────────────────────
# Each tag is rendered as a fixed-width colored bracket label.

_TAG_STYLES: dict[str, str] = {
    "cached":     "2",     # dim
    "download":   "36",    # cyan
    "verify":     "33",    # yellow
    "extract":    "34",    # blue
    "patch":      "1;35",  # bold magenta
    "build dir":  "2",     # dim
    "build":      "1;34",  # bold blue
    "run":        "2",     # dim
    "debug":      "35",    # magenta
    "warn":       "33",    # yellow
    "error":      "1;31",  # bold red
}

_TAG_WIDTH = max(len(k) for k in _TAG_STYLES) + 2  # "[build dir]" + padding


def tag(name: str) -> str:
    """Return a colored, fixed-width [tag] string."""
    code = _TAG_STYLES.get(name, "2")
    label = _c(code, f"[{name}]")
    # Pad so that content after the tag always starts at the same column.
    # Padding is added as plain spaces (no color codes) for correct width.
    pad = " " * (_TAG_WIDTH - len(f"[{name}]"))
    return label + pad
