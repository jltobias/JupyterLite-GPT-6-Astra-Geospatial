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

The original splash embeds no font files, external artwork, basemap or trademark logo. The project does not distribute the supplied presentations, papers, external demos or Overture data. Any added dataset needs exact release, publisher, attribution, license and modification records; the repository's MIT license does not apply to external material.

The 3D scene HTML embeds synthetic data or the attributed OSM/terrain extracts described below, plus original application code. Renderer distributions are loaded from pinned CDN URLs, not committed to this repository. Preserve each distribution's complete notices if vendoring for offline use. No live basemap, terrain tile service, geocoder or paid map service is needed by the scenes; the terrain extension uses a bundled derivative of a public terrain tile.

## Bundled data extracts

These assets are not covered by the repository MIT license. Exact URLs, retrieval/acquisition records and transformations accompany each JSON/GeoJSON file; see [data provenance](content/data/README.md).

- **OpenStreetMap:** © OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), [copyright and attribution](https://www.openstreetmap.org/copyright). The extract and modifications remain available in editable GeoJSON under ODbL. Retain attribution and applicable share-alike obligations when redistributing derived databases.
- **Sentinel-2:** contains modified Copernicus Sentinel data (2025), processed by ESA; COG distribution by Element 84. [Sentinel Data Legal Notice](https://sentinels.copernicus.eu/documents/247904/690755/Sentinel_Data_Legal_Notice). Red/NIR reflectance is resampled and scaled; SCL accompanies the chip.
- **Mapzen terrain:** Mapzen; USGS SRTM/GMTED2010 and NOAA ETOPO1 terrain sources. Preserve the [source-specific attribution and terms](https://github.com/tilezen/joerd/blob/master/docs/attribution.md). The bundled array is a decoded and subsampled Terrarium tile, not an original survey.

Optional desktop data preparation uses Rasterio (BSD-3-Clause) and Pillow (HPND/PIL terms); preserve their distribution notices when redistributing those dependencies. They are not notebook runtime requirements.
