# Platform tags and what they imply

Wheel filename tags encode ABI and platform. Use them as evidence for whether
native compilation is required — not as the sole source of truth.

## Common tags

| Tag pattern | Meaning | Packaging implication |
|-------------|---------|------------------------|
| `py3-none-any` | Pure Python, any platform | Low build complexity; source or wheel both fine |
| `py2.py3-none-any` | Universal pure Python (legacy) | Same as above |
| `cp311-cp311-manylinux*` | CPython 3.11, Linux manylinux | Built native extension; needs matching ABI |
| `cp311-cp311-macosx_*` | macOS native wheel | Platform-specific compile / link |
| `cp311-cp311-win_amd64` | Windows native wheel | Platform-specific compile / link |
| `*-musllinux_*` | musl-based Linux | Distinct from glibc manylinux |

## How to use tags in investigations

- **Only `py3-none-any` on PyPI** → strong signal of pure Python; still confirm
  there is no optional extension module gated behind extras.
- **manylinux / macosx / win wheels present** → expect a C/C++/Rust/Fortran
  toolchain for source builds, plus any linked system libraries.
- **Multiple platform wheels, no sdist** → source builds may be unsupported;
  call that out explicitly.
- **Do not confuse** runtime GPU wheels (e.g. CUDA-flavored PyTorch deps) with
  this package's own need to compile native code.

## Related signals (when tags are missing)

- `setup.py` `ext_modules` / Cython / cmake / meson
- `package-info` or README mentioning BLAS, LAPACK, OpenMP, CUDA, MPI
- CI matrices building wheels per OS/arch
