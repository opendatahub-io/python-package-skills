# Common Python build system patterns

Use this reference when classifying how a package is built. Prefer evidence from
repository files over PyPI blurb text.

## How to identify the backend

1. Read `[build-system]` in `pyproject.toml` (`requires`, `build-backend`).
2. Check for `setup.py` / `setup.cfg` even when `pyproject.toml` exists — custom
   `ext_modules`, cmake hooks, or dynamic deps often live there.
3. Look for sibling build systems: `meson.build`, `CMakeLists.txt`,
   `Cargo.toml`, `Makefile` used by extension builds.

## Common backends

| Backend | Signals | Notes |
|---------|---------|-------|
| setuptools | `setuptools.build_meta`, `setup.py`, `setup.cfg` | Still the most common for packages with `ext_modules` |
| flit / hatchling | `flit_core`, `hatchling` | Often pure Python; confirm no native hooks |
| poetry | `poetry.core.masonry.api` | Check for build scripts / extensions |
| meson-python | `mesonpy`, `meson.build` | Native code common; needs compilers + pkg-config |
| scikit-build-core / cmake | `scikit_build_core`, `CMakeLists.txt` | C/C++/Fortran; system libs likely |
| maturin | `maturin`, `Cargo.toml` | Rust extensions |

## Red flags for underestimating complexity

- `ext_modules`, Cython `.pyx`, SWIG, or `pybind11` usage
- Vendored third-party C trees or `libs/` with compile scripts
- Environment variables that select CUDA / ROCm / CPU at build time
- Narrow pins on compilers, CUDA toolkit, or BLAS implementations
- Build files not at repo root (monorepo / subdirectory package)

## Monorepos

If `setup.py` / `pyproject.toml` for the target package is **not** at the
repository root, record the exact subdirectory path. Downstream builders look
at the repo root by default and will fail without `prepare_source` guidance.
