from __future__ import annotations

import pytest

from seth.resolver import (
    Constraint,
    DepSpec,
    PlannedStep,
    _parse_ver,
    build_install_plan,
    parse_dep,
    resolve_version,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _write(formula_dir, name, versions, deps=None, build_deps=None):
    """Write a minimal formula file into formula_dir."""
    versions_body = "\n        ".join(
        f'"{v}": {{"url": "", "sha256": ""}},' for v in versions
    )
    latest = list(versions)[0]
    deps_repr = repr(deps or [])
    build_deps_repr = repr(build_deps or [])
    cls = "".join(p.capitalize() for p in name.replace("-", "_").split("_"))
    (formula_dir / f"{name}.py").write_text(
        f"from seth.formula import Formula\n\n"
        f"class {cls}Formula(Formula):\n"
        f"    name = {name!r}\n"
        f"    latest = {latest!r}\n"
        f"    dependencies = {deps_repr}\n"
        f"    build_dependencies = {build_deps_repr}\n"
        f"    versions = {{\n        {versions_body}\n    }}\n"
    )


# ── parse_dep / Constraint ─────────────────────────────────────────────────────

def test_parse_dep_no_constraint():
    d = parse_dep("openssl")
    assert d.name == "openssl"
    assert d.constraints == []


def test_parse_dep_single_constraint():
    d = parse_dep("openssl>=3.0")
    assert d.name == "openssl"
    assert len(d.constraints) == 1
    assert d.constraints[0].op == ">="
    assert d.constraints[0].version == (3, 0)


def test_parse_dep_multiple_constraints():
    d = parse_dep("openssl>=3.0,<4")
    assert len(d.constraints) == 2
    ops = {c.op for c in d.constraints}
    assert ops == {">=", "<"}


def test_parse_dep_pinned():
    d = parse_dep("zlib==1.3.2")
    assert d.constraints[0].op == "=="
    assert d.constraints[0].version == (1, 3, 2)


def test_parse_dep_invalid_name_raises():
    with pytest.raises(ValueError, match="Cannot parse"):
        parse_dep(">=3.0")


@pytest.mark.parametrize("op,ver,candidate,expected", [
    ("==", "1.0.0", "1.0.0", True),
    ("==", "1.0.0", "1.0.1", False),
    ("!=", "1.0.0", "1.0.1", True),
    ("!=", "1.0.0", "1.0.0", False),
    (">=", "1.0.0", "1.0.0", True),
    (">=", "1.0.0", "0.9.9", False),
    ("<=", "1.0.0", "1.0.0", True),
    ("<=", "1.0.0", "1.0.1", False),
    (">",  "1.0.0", "1.0.1", True),
    (">",  "1.0.0", "1.0.0", False),
    ("<",  "2.0",   "1.9.9", True),
    ("<",  "2.0",   "2.0",   False),
])
def test_constraint_satisfied_by(op, ver, candidate, expected):
    c = Constraint(op, _parse_ver(ver))
    assert c.satisfied_by(candidate) == expected


def test_constraint_compatible_two_part():
    # ~=1.3 → >=1.3, <2
    c = Constraint("~=", (1, 3))
    assert c.satisfied_by("1.3") is True
    assert c.satisfied_by("1.9.9") is True
    assert c.satisfied_by("2.0") is False
    assert c.satisfied_by("1.2.9") is False


def test_constraint_compatible_three_part():
    # ~=1.3.1 → >=1.3.1, <1.4
    c = Constraint("~=", (1, 3, 1))
    assert c.satisfied_by("1.3.1") is True
    assert c.satisfied_by("1.3.9") is True
    assert c.satisfied_by("1.4.0") is False
    assert c.satisfied_by("1.3.0") is False


def test_dep_spec_satisfied_by_all_constraints():
    d = parse_dep("pkg>=1.0,<2.0")
    assert d.satisfied_by("1.5") is True
    assert d.satisfied_by("2.0") is False
    assert d.satisfied_by("0.9") is False


# ── resolve_version ────────────────────────────────────────────────────────────

def test_resolve_version_picks_latest_when_no_constraint(formula_dir, isolated_config):
    _write(formula_dir, "foo", ["2.0.0", "1.0.0"])
    spec = parse_dep("foo")
    assert resolve_version(spec) == "2.0.0"


def test_resolve_version_respects_constraint(formula_dir, isolated_config):
    _write(formula_dir, "foo", ["2.0.0", "1.5.0", "1.0.0"])
    spec = parse_dep("foo<2.0")
    assert resolve_version(spec) == "1.5.0"


def test_resolve_version_no_matching_version_raises(formula_dir, isolated_config):
    _write(formula_dir, "foo", ["1.0.0"])
    spec = parse_dep("foo>=9.0")
    with pytest.raises(ValueError, match="No version of 'foo'"):
        resolve_version(spec)


def test_resolve_version_no_formula_raises(formula_dir, isolated_config):
    spec = parse_dep("does-not-exist")
    with pytest.raises(FileNotFoundError):
        resolve_version(spec)


# ── build_install_plan ────────────────────────────────────────────────────────

def test_plan_single_package_no_deps(formula_dir, isolated_config):
    _write(formula_dir, "solo", ["1.0.0"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("solo"))
    assert len(plan) == 1
    assert plan[0].formula.name == "solo"
    assert plan[0].build_only is False
    assert plan[0].direct_deps == {}


def test_plan_topological_order(formula_dir, isolated_config):
    _write(formula_dir, "c", ["1.0.0"])
    _write(formula_dir, "b", ["1.0.0"], deps=["c"])
    _write(formula_dir, "a", ["1.0.0"], deps=["b"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("a"))
    names = [s.formula.name for s in plan]
    assert names == ["c", "b", "a"]


def test_plan_build_only_dep_marked_correctly(formula_dir, isolated_config):
    _write(formula_dir, "tool", ["1.0.0"])
    _write(formula_dir, "lib", ["1.0.0"])
    _write(formula_dir, "pkg", ["1.0.0"], deps=["lib"], build_deps=["tool"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("pkg"))
    tool_step = next(s for s in plan if s.formula.name == "tool")
    lib_step  = next(s for s in plan if s.formula.name == "lib")
    assert tool_step.build_only is True
    assert lib_step.build_only is False


def test_plan_build_dep_becomes_runtime_when_needed_by_both(formula_dir, isolated_config):
    _write(formula_dir, "shared", ["1.0.0"])
    _write(formula_dir, "pkg", ["1.0.0"], deps=["shared"], build_deps=["shared"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("pkg"))
    shared_step = next(s for s in plan if s.formula.name == "shared")
    assert shared_step.build_only is False


def test_plan_cycle_raises(formula_dir, isolated_config):
    _write(formula_dir, "a", ["1.0.0"], deps=["b"])
    _write(formula_dir, "b", ["1.0.0"], deps=["a"])
    from seth.formula import load_formula
    with pytest.raises(ValueError, match="Circular dependency"):
        build_install_plan(load_formula("a"))


def test_plan_direct_deps_populated(formula_dir, isolated_config):
    _write(formula_dir, "dep", ["1.0.0"])
    _write(formula_dir, "pkg", ["1.0.0"], deps=["dep"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("pkg"))
    pkg_step = next(s for s in plan if s.formula.name == "pkg")
    assert pkg_step.direct_deps == {"dep": "1.0.0"}


def test_plan_diamond_same_version_no_duplicate(formula_dir, isolated_config):
    """X and Z both depend on Y@same version → Y appears once in the plan."""
    _write(formula_dir, "y", ["1.0.0"])
    _write(formula_dir, "x", ["1.0.0"], deps=["y"])
    _write(formula_dir, "z", ["1.0.0"], deps=["y"])
    _write(formula_dir, "w", ["1.0.0"], deps=["x", "z"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("w"))
    y_steps = [s for s in plan if s.formula.name == "y"]
    assert len(y_steps) == 1


def test_plan_diamond_different_versions_both_built(formula_dir, isolated_config):
    """X→Y@1.0 and Z→Y@1.1 should both end up in the plan without raising."""
    _write(formula_dir, "y", ["1.0.1", "1.0.0"])
    _write(formula_dir, "x", ["1.0.0"], deps=["y==1.0.0"])
    _write(formula_dir, "z", ["1.0.0"], deps=["y==1.0.1"])
    _write(formula_dir, "w", ["1.0.0"], deps=["x", "z"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("w"))
    y_versions = {s.formula.version for s in plan if s.formula.name == "y"}
    assert y_versions == {"1.0.0", "1.0.1"}


def test_plan_diamond_different_versions_direct_deps(formula_dir, isolated_config):
    """Each consumer records the correct y version in its direct_deps."""
    _write(formula_dir, "y", ["1.0.1", "1.0.0"])
    _write(formula_dir, "x", ["1.0.0"], deps=["y==1.0.0"])
    _write(formula_dir, "z", ["1.0.0"], deps=["y==1.0.1"])
    _write(formula_dir, "w", ["1.0.0"], deps=["x", "z"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("w"))
    x_step = next(s for s in plan if s.formula.name == "x")
    z_step = next(s for s in plan if s.formula.name == "z")
    assert x_step.direct_deps["y"] == "1.0.0"
    assert z_step.direct_deps["y"] == "1.0.1"


def test_plan_constraint_reuses_compatible_already_planned(formula_dir, isolated_config):
    """If Y>=1.0 is already planned at 1.0.1, don't build a second copy."""
    _write(formula_dir, "y", ["1.0.1", "1.0.0"])
    _write(formula_dir, "x", ["1.0.0"], deps=["y>=1.0"])
    _write(formula_dir, "z", ["1.0.0"], deps=["y>=1.0"])
    _write(formula_dir, "w", ["1.0.0"], deps=["x", "z"])
    from seth.formula import load_formula
    plan = build_install_plan(load_formula("w"))
    y_steps = [s for s in plan if s.formula.name == "y"]
    assert len(y_steps) == 1
