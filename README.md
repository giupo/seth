# seth

A source-based package manager for Linux, inspired by Homebrew.  
Designed for environments where you need up-to-date software without root access — tested on RHEL 8 / Osiride.

---

## How it works

seth builds packages from source and installs them into a versioned **keg**:

```
~/.local/seth/
  Cellar/
    openssl/3.3.2/          ← keg: self-contained install prefix
    zlib/1.3.2/
    curl/8.20.0/
  bin/                      ← symlinks into the active keg versions
  lib/
  include/
  ...
```

Each package lives in its own keg. **Linking** creates symlinks from the root prefix (`~/.local/seth/`) into the active keg. Multiple versions can coexist; only one is linked at a time.

---

## Installation

```bash
# Clone the repo
git clone <url> ~/projects/seth
cd ~/projects/seth

# Install in development mode (editable)
pip install -e .

# Or build a single self-contained executable
make pyz
cp dist/seth.pyz ~/.local/bin/seth
chmod +x ~/.local/bin/seth
```

**Requirements:** Python ≥ 3.10, `patch`, `make`, `cmake` (for cmake-based packages), `git` (for `seth update`).

---

## First-time setup

```bash
seth init
```

Interactive wizard that asks for:
- **Root prefix** — where packages are installed (default: `~/.local/seth`)
- **Cellar** — where kegs are stored (default: `<root>/Cellar`)
- **Remote formulas URL** — git repo or tar.gz with formula files (optional)

After init, add seth to your shell environment:

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(seth env)"
```

If you provided a formulas URL, init will offer to fetch them immediately. You can update later with `seth update`.

---

## Commands

### Package management

```bash
seth install <pkg>[@<version>]   # build and link a package
seth uninstall <pkg>[@<version>] # remove a package
seth upgrade <pkg>[@<version>]   # rebuild and relink at a newer version
```

seth resolves the full dependency graph, performs a topological sort, and builds each missing dependency in order before the requested package.

```bash
# Examples
seth install curl          # installs zlib, perl, openssl, pkgconfig, then curl
seth install gcc@16.1.0
seth install curl --force  # reinstall even if already present
seth install curl --no-link  # build into cellar without symlinking
seth install curl --debug    # keep build directory after install for inspection
```

### Linking

```bash
seth link <pkg>[@<version>]    # symlink a keg into the root prefix
seth unlink <pkg>              # remove symlinks from the root prefix
```

seth tracks every file it links in the database. Unlinking reads this list and removes exactly those symlinks — no keg access required, no fragile path comparisons.

### Information

```bash
seth list              # show all installed packages and their link status
seth info <pkg>        # show versions, dependencies, install status
seth search <term>     # search available formulas by name
seth available         # list all available formulas
seth config            # show current configuration
seth env               # print shell environment variable exports
```

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

---

## Build environment

During every build, seth prepares the environment so that previously installed packages are visible to configure scripts and the compiler:

| Variable | Purpose |
|---|---|
| `PATH` | seth `bin/` and `sbin/` prepended |
| `PKG_CONFIG_PATH` | seth `lib/pkgconfig` and `share/pkgconfig` |
| `LIBRARY_PATH` | seth `lib/` and `lib64/` (compile-time linker search) |
| `CPPFLAGS` | `-I<root>/include` |
| `LDFLAGS` | `-L<root>/lib -L<root>/lib64` + `-Wl,-rpath,<root>/lib` |
| `ACLOCAL_PATH` | seth `share/aclocal` |

`LD_LIBRARY_PATH` is intentionally **not** set during builds. Setting it would cause the system compiler's internal tools (e.g. `cc1`) to load seth-installed versions of `libgmp`, `libmpfr`, `libmpc` instead of the system versions they were compiled against, breaking the build. `-Wl,-rpath` is used instead so that compiled binaries find their seth dependencies at runtime without polluting the system loader path.

---

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

## Available formulas

| Package | Latest | Dependencies |
|---|---|---|
| curl | 8.20.0 | openssl, zlib, perl, pkgconfig |
| emacs | — | ncurses, libxml2, gnutls |
| gcc | 16.1.0 | gmp, mpfr, mpc, zlib |
| gmp | 6.3.0 | — |
| gnutls | 3.8.8 | nettle, libtasn1, gmp |
| imagemagick | 7.1.1-47 | zlib |
| libevent | 2.1.12 | openssl |
| libssh2 | 1.11.1 | openssl, zlib |
| libtasn1 | 4.19.0 | — |
| libxml2 | 2.12.9 | zlib |
| mpc | 1.3.1 | gmp, mpfr |
| mpfr | 4.2.2 | gmp |
| ncurses | 6.5 | — |
| nettle | 3.9.1 | gmp |
| openssl | 3.3.2 | zlib, perl |
| perl | — | zlib |
| pkgconfig | 0.29.2 | — |
| tmux | 3.5a | libevent, ncurses |
| wget | 1.21.4 | openssl |
| zlib | 1.3.2 | — |

---

## Single-file executable

seth can be packaged as a self-contained `.pyz` file (Python zipapp):

```bash
make pyz          # produces dist/seth.pyz
make clean        # remove dist/
```

The `.pyz` contains only the `seth/` package — formulas live in the remote repository fetched by `seth update`. Running from a `.pyz` automatically disables the bundled `formulas/` directory.

```bash
cp dist/seth.pyz ~/.local/bin/seth
seth init         # first-time setup: configure root, fetch formulas
```

---

## Configuration

seth reads `~/.config/seth/seth.conf` (INI format). All values can be overridden with environment variables.

```ini
[paths]
root    = /opt/seth          ; SETH_ROOT
cellar  = /data/seth/Cellar  ; SETH_CELLAR (default: <root>/Cellar)
formulas = /my/formulas      ; SETH_FORMULAS (overrides remote cache + bundled)

[formulas]
url = https://github.com/acme/seth-formulas  ; SETH_FORMULAS_URL
```

`seth config` shows the active configuration. `seth env` prints the shell exports needed to use seth-installed packages.

---

## License

Copyright (C) 2026 Giuseppe Acito \<giuseppe.acito@gmail.com\>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See [LICENSE](LICENSE) for the full text.
