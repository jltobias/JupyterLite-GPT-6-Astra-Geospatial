# Third-party notices

This identifies principal dependencies; retain full notices in their distributions, including transitive components.

| Component | Role | Upstream license / notices |
|---|---|---|
| JupyterLite | Notebook interface | BSD-3-Clause; [license](https://github.com/jupyterlite/jupyterlite/blob/main/LICENSE) |
| Pyodide kernel | Kernel integration | BSD-3-Clause; [license](https://github.com/jupyterlite/pyodide-kernel/blob/main/LICENSE) |
| Pyodide | Browser Python | MPL-2.0 and bundled component licenses; [license](https://github.com/pyodide/pyodide/blob/main/LICENSE) |
| CPython | Interpreter | PSF and bundled notices; [license](https://docs.python.org/3/license.html) |
| NumPy | Arrays | BSD-3-Clause and bundled notices; [license](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| Matplotlib | Plots | PSF-based Matplotlib terms and historical notices; [license](https://matplotlib.org/stable/project/license.html) |
| IPython / ipykernel / nbformat / nbclient | Display and validation | BSD-3-Clause; [IPython](https://github.com/ipython/ipython), [ipykernel](https://github.com/ipython/ipykernel), [nbformat](https://github.com/jupyter/nbformat), [nbclient](https://github.com/jupyter/nbclient) |
| Jupyter Server / JupyterLab Server | Build-time indexing | BSD-3-Clause; [server](https://github.com/jupyter-server/jupyter_server/blob/main/LICENSE), [lab server](https://github.com/jupyterlab/jupyterlab_server/blob/main/LICENSE) |
| Jupyter Book | Reading companion | BSD-3-Clause; [v1 source](https://github.com/jupyter-book/jupyter-book/tree/v1.0.4.post1) |
| Sphinx / MyST / themes | Book dependencies | Preserve notices in exact installed distributions |
| Rust | WASM compilation | MIT OR Apache-2.0 and component notices; [licensing](https://github.com/rust-lang/rust#license) |
| Wasmtime | Desktop validation | Apache-2.0 WITH LLVM-exception; [license](https://github.com/bytecodealliance/wasmtime/blob/main/LICENSE) |
| Playwright | Browser tests | Apache-2.0; [license](https://github.com/microsoft/playwright/blob/main/LICENSE) |

The original Rust kernel has no third-party crates. Its binary may include standard-library/compiler support; Rust MIT and Apache texts are retained in `licenses/`. Retain toolchain component notices when rebuilding or expanding the binary. Browser runtime and scientific wheels are downloaded from upstream services rather than committed here.

The original splash embeds no font files, external artwork, basemap or trademark logo. The project does not distribute the supplied presentations, papers, external demos, OSM or Overture data. Any added dataset needs exact release, publisher, attribution, license and modification records; the repository's MIT license does not apply to external material.
