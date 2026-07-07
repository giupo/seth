# seth-formulas

This is the repository for the formulas used by seth (https://github.com/giupo/seth)


### Formula management

```bash
seth edit <pkg>        # open formula in $EDITOR
                       # if the formula doesn't exist, opens a template
                       # file is written only when you save from the editor
```

### Repository

```bash
seth update            # fetch/pull the remote formula repository
                       # supports git clone/pull or tar.gz download
```


## Formulas

A formula is a Python file in the `formulas/` directory (or in the remote formula repository fetched by `seth update`).

### Minimal example

```python
from seth.formula import Formula

class ZlibFormula(Formula):
    name = "zlib"
    latest = "1.3.2"

    versions = {
        "1.3.2": {
            "url": "https://zlib.net/zlib-1.3.2.tar.gz",
            "sha256": "bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16",
        },
    }
```

### All fields

```python
class MyPkgFormula(Formula):
    name = "mypkg"
    latest = "1.0.0"

    # runtime deps — built and linked before this package
    dependencies = ["openssl", "zlib"]
    # compile-time only — built and linked for the build, not recorded as runtime deps
    build_dependencies = ["pkgconfig", "cmake"]

    # "autoconf" (default), "cmake", "meson", or "custom"
    build_system = "autoconf"

    # appended to the default configure/cmake/meson args
    extra_configure_args = ["--enable-foo"]

    versions = {
        "1.0.0": {"url": "...", "sha256": "..."},
        "0.9.0": {"url": "...", "sha256": "..."},
    }

    # override configure/cmake/meson args entirely
    def configure_args(self):
        return [f"--prefix={self.keg}", "--enable-shared"]

    # source-level patches applied before the build
    # files: patches/<name>/0001-fix-something.patch  (unified diff, patch -p1)
    patches = ["0001-fix-something.patch"]

    # programmatic patch for cases where a unified diff is awkward
    def patch(self, source_dir):
        f = source_dir / "src" / "broken.c"
        f.write_text(f.read_text().replace("old_thing", "new_thing"))

    def post_install(self):
        # runs after make install, inside the keg
        pass
```

### Build systems

| `build_system` | What seth runs |
|---|---|
| `autoconf` (default) | `./configure <args>` → `make -j<n>` → `make install` |
| `cmake` | `cmake .. <args>` → `make -j<n>` → `make install` |
| `meson` | `meson setup _build <args>` → `ninja -C _build` → `ninja install` |
| `custom` | calls `formula.build(source_dir)` — you run everything |

### Dependency version constraints

```python
dependencies = ["openssl>=3.0", "zlib>=1.2"]
```

### Patches

Two mechanisms, both applied before the build starts:

**File-based** (unified diff, stored in `patches/<name>/`):
```python
patches = ["0001-fix-bool-keyword.patch"]
```

**Programmatic** (Python, for simple substitutions or when line numbers aren't stable):
```python
def patch(self, source_dir):
    f = source_dir / "glib" / "goption.c"
    f.write_text(f.read_text().replace("gboolean bool;", "gboolean _bool;"))
```

---

## License

Copyright (C) 2026 Giuseppe Acito \<giuseppe.acito@gmail.com\>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for the full text.
