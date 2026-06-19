"""
Defines some types used here and there
"""

from enum import StrEnum


class BuildType(StrEnum):
    """Build systems supported by Formula.build_system / builder.build().

    AUTOGEN  — runs ./autogen.sh, then ./configure, then make/make install.
    AUTOCONF — runs ./configure, then make/make install (the common case).
    MAKE     — no configure step; bare Makefile projects (e.g. bzip2) that
               take their settings (PREFIX, CC, ...) as make variables.
    CMAKE    — runs cmake in a _build subdir, then make/make install.
    MESON    — runs meson setup in a _build subdir, then ninja/ninja install.
    CUSTOM   — delegates entirely to the formula's own build() method.
    """

    AUTOGEN = "autogen"
    AUTOCONF = "autoconf"
    MAKE = "make"
    CMAKE = "cmake"
    MESON = "meson"
    CUSTOM = "custom"
