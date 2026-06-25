"""
Dependency resolver: version constraints, cycle detection, topological sort.

Dependency spec syntax:
  "openssl"           any version
  "openssl>=3.0"      at least 3.0
  "openssl~=3.3"      compatible with 3.3  (>=3.3, <4)
  "openssl~=3.3.1"    compatible with 3.3.1 (>=3.3.1, <3.4)
  "openssl>=3.0,<4"   multiple constraints, comma-separated

Supported operators: == != >= <= > < ~=
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .formula import Formula

# ── version arithmetic ────────────────────────────────────────────────────────

def _parse_ver(s: str) -> tuple[int, ...]:
    try:
        return tuple(int(p) for p in s.strip().split("."))
    except ValueError:
        raise ValueError(f"Cannot parse version: {s!r}")


def _cmp(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    n = max(len(a), len(b))
    a += (0,) * (n - len(a))
    b += (0,) * (n - len(b))
    return (a > b) - (a < b)


# ── constraints ───────────────────────────────────────────────────────────────

_OP_RE = re.compile(r"^(~=|==|!=|>=|<=|>|<)")


@dataclass
class Constraint:
    op: str
    version: tuple[int, ...]

    def satisfied_by(self, v: str) -> bool:
        c = _cmp(_parse_ver(v), self.version)
        match self.op:
            case "==": return c == 0
            case "!=": return c != 0
            case ">=": return c >= 0
            case "<=": return c <= 0
            case ">":  return c > 0
            case "<":  return c < 0
            case "~=": return self._compatible(v)
            case _: raise ValueError(f"Unknown operator: {self.op!r}")

    def _compatible(self, v: str) -> bool:
        # ~=X.Y.Z → >=X.Y.Z, <X.Y+1
        # ~=X.Y   → >=X.Y,   <X+1
        parsed = _parse_ver(v)
        if _cmp(parsed, self.version) < 0:
            return False
        prefix = self.version[:-1]
        upper = (self.version[0] + 1,) if not prefix else prefix[:-1] + (prefix[-1] + 1,)
        return _cmp(parsed, upper) < 0

    def __str__(self) -> str:
        return f"{self.op}{'.'.join(str(x) for x in self.version)}"


# ── dep spec ──────────────────────────────────────────────────────────────────

_NAME_RE = re.compile(r"^([A-Za-z0-9_\-]+)")


@dataclass
class DepSpec:
    name: str
    constraints: list[Constraint] = field(default_factory=list)

    def satisfied_by(self, version: str) -> bool:
        return all(c.satisfied_by(version) for c in self.constraints)

    def __str__(self) -> str:
        return self.name + "".join(str(c) for c in self.constraints)


def parse_dep(spec: str) -> DepSpec:
    spec = spec.strip()
    m = _NAME_RE.match(spec)
    if not m:
        raise ValueError(f"Cannot parse dependency spec: {spec!r}")
    name = m.group(1)
    rest = spec[len(name):]

    constraints: list[Constraint] = []
    for part in rest.split(","):
        part = part.strip()
        if not part:
            continue
        om = _OP_RE.match(part)
        if not om:
            raise ValueError(f"Cannot parse constraint {part!r} in {spec!r}")
        op = om.group(1)
        constraints.append(Constraint(op, _parse_ver(part[len(op):])))

    return DepSpec(name, constraints)


# ── version resolution ────────────────────────────────────────────────────────

def resolve_version(spec: DepSpec) -> str:
    """
    Return the best version for the given spec.
    Prefers the currently linked version when it satisfies constraints
    (avoids unnecessary rebuilds).
    """
    from . import cellar
    from .formula import available_versions

    candidates = available_versions(spec.name)
    if not candidates:
        raise ValueError(f"No formula versions available for '{spec.name}'")

    if not spec.constraints:
        # No constraints: prefer linked, else take newest
        linked = cellar.linked_version(spec.name)
        return linked if linked else candidates[0]

    linked = cellar.linked_version(spec.name)
    if linked and spec.satisfied_by(linked):
        return linked

    for ver in candidates:          # newest first
        if spec.satisfied_by(ver):
            return ver

    raise ValueError(
        f"No version of '{spec.name}' satisfies '{spec}'. "
        f"Available: {', '.join(candidates)}"
    )


# ── install plan ──────────────────────────────────────────────────────────────

@dataclass
class PlannedStep:
    formula: Formula
    build_only: bool = False
    # Direct dependencies of *this* step, resolved to the exact version chosen
    # for this install plan: {dep_name: dep_version}. Lets the builder point
    # each dependency's include/lib/rpath at its specific keg instead of the
    # shared root prefix, so two consumers in the same plan can depend on
    # different versions of the same package without conflicting.
    direct_deps: dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        tag = " [build only]" if self.build_only else ""
        return f"{self.formula.name} {self.formula.version}{tag}"


def build_install_plan(root: Formula) -> list[PlannedStep]:
    """
    Return the full install plan for *root* (dependencies first, root last).

    Guarantees:
    - Topological order (each dep appears before its dependents)
    - Cycle detection (raises ValueError with the cycle path)
    - If the same package is needed as both build-only and runtime,
      it is marked as runtime (least restrictive wins)
    - Different branches may resolve the same dependency to different
      versions; both are planned and built rather than rejected as a
      conflict (each step's `direct_deps` records exactly which version
      it should build/link against).
    """
    plan: list[PlannedStep] = []
    _visit(root, path=[], plan=plan, build_only=False)
    return plan


def _visit(
    formula: Formula,
    path: list[str],
    plan: list[PlannedStep],
    build_only: bool,
) -> None:
    name = formula.name
    version = formula.version

    # Exact (name, version) already in plan → just possibly upgrade build→runtime
    existing = next(
        (s for s in plan if s.formula.name == name and s.formula.version == version),
        None,
    )
    if existing:
        if existing.build_only and not build_only:
            existing.build_only = False
        return

    # Cycle detection (package-level, regardless of version)
    if name in path:
        cycle = " → ".join(path + [name])
        raise ValueError(f"Circular dependency: {cycle}")

    new_path = path + [name]

    all_deps: list[tuple[str, bool]] = (
        [(d, False) for d in getattr(formula, "dependencies", [])]
        + [(d, True)  for d in getattr(formula, "build_dependencies", [])]
    )

    direct_deps: dict[str, str] = {}

    for dep_str, is_build in all_deps:
        spec = parse_dep(dep_str)

        # Reuse an already-planned version of this dependency if it satisfies
        # the constraint, instead of always resolving fresh. Avoids building
        # the same package twice when one version happens to satisfy both.
        compatible = next(
            (s for s in plan
             if s.formula.name == spec.name and spec.satisfied_by(s.formula.version)),
            None,
        )
        if compatible:
            if compatible.build_only and not is_build:
                compatible.build_only = False
            direct_deps[spec.name] = compatible.formula.version
            continue

        ver = resolve_version(spec)
        from .formula import load_formula
        dep_formula = load_formula(spec.name, ver)
        _visit(dep_formula, new_path, plan, is_build)
        direct_deps[spec.name] = ver

    plan.append(PlannedStep(formula=formula, build_only=build_only, direct_deps=direct_deps))
