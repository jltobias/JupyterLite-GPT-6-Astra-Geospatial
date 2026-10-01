# Validation record

Initial validation: October 1, 2026.

| Check | Evidence |
|---|---|
| Desktop notebook execution | All 10 notebooks executed with fresh namespaces, schema validation and embedded assertions |
| Shared numerical contracts | Population conservation, invalid weights, coordinate round trips, disconnected graph paths, scenario parity, malformed model responses |
| Rust/WASM | Compiled from the included Rust source; Wasmtime and browser results agree with the Python reference within `rtol=1e-11` |
| Actual browser runtime | All 10 notebooks executed in JupyterLite/Pyodide with completed code cells, no error outputs and one plot per notebook |
| Static site | JupyterLite 0.8.5 and Pyodide kernel 0.8.6 built successfully |
| JupyterBook | Jupyter Book 1.0.4.post1 / Sphinx build succeeded with warnings treated as errors; includes plots captured during desktop validation |
| Visual review | Book landing page and original SVG splash inspected in the browser |

The browser suite executes the actual notebook cells through the JupyterLab application and kernel APIs. It does not substitute desktop Python for the Pyodide execution. `scripts/browser_check.py` is the CI version. `scripts/browser_runner.html` is an optional visible local runner: copy it to `_site/check.html`, serve the site, wait for the embedded launcher and press **Run all notebook checks**. Do not ship local diagnostic copies unintentionally.

CI results are authoritative for each pushed revision: see [GitHub Actions](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial/actions). Validation reports and browser screenshots are retained in its `validation-results` artifact. Local Windows restrictions prevented launching Playwright as a subprocess, so initial browser execution used the visible runner in the in-app browser. The CI Playwright path runs independently on Linux.

No live GPT-6 Astra API evaluation was performed. Notebook 09's initial answer is a labeled fixture, not measured model performance. No real urban dataset, epidemiological calibration, external-validity assessment or fully offline deployment test was performed. Timings are device-specific and are not general Rust-versus-Python claims.
