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
| MapLibre GL JS 5.6.1 | Notebook 14 geographic 3D scene; downloaded from unpkg | BSD-3-Clause; [license](https://github.com/maplibre/maplibre-gl-js/blob/v5.6.1/LICENSE.txt) |
| deck.gl 9.1.14 | Notebook 15 polygon/path/facility layers; downloaded from unpkg | MIT and transitive notices; [license](https://github.com/visgl/deck.gl/blob/v9.1.14/LICENSE) |
| Plotly.js 3.1.0 | Notebook 16 3D surface; downloaded from cdn.plot.ly | MIT and transitive notices; [license](https://github.com/plotly/plotly.js/blob/v3.1.0/LICENSE) |

The original Rust kernel has no third-party crates. Its binary may include standard-library/compiler support; Rust MIT and Apache texts are retained in `licenses/`. Retain toolchain component notices when rebuilding or expanding the binary. Browser runtime and scientific wheels are downloaded from upstream services rather than committed here.

The original splash embeds no font files, external artwork, basemap or trademark logo. The project does not distribute the supplied presentations, papers, external demos, OSM or Overture data. Any added dataset needs exact release, publisher, attribution, license and modification records; the repository's MIT license does not apply to external material.

The 3D scene HTML embeds only original synthetic data and application code. Renderer distributions are loaded from pinned CDN URLs, not committed to this repository. Preserve each distribution's complete notices if vendoring for offline use. No external basemap, terrain tiles, geocoder or paid map service is used by these scenes.
