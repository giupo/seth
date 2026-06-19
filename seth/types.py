"""
Defines some types used here and there
"""

from enum import StrEnum

class BuildType(StrEnum):
    AUTOGEN = "autogen"
    AUTOCONF = "autoconf"
    MAKE = "make"
    CMAKE = "cmake"
    MESON = "meson"
    CUSTOM = "custom"
