# Validation record

## Implemented notebook extensions — October 2, 2026

Expanded all sixteen existing notebooks in place; no notebooks were added in this revision. Each now has a four-branch concept map, a runnable investigation, spatial comparison graphics, evidence-only prompt/image exports, and a scored-response workflow that defaults to **NOT RUN**. The original implementation briefs remain as review criteria. See the teaching guide for the investigation-by-notebook inventory.

Selected investigations now use three small public-data extracts: 125 OSM footprints, a 64 × 64 Sentinel-2 red/NIR/SCL chip, and a 32 × 32 terrain chip. Source IDs, processing, units, dates and attribution accompany the data. Synthetic population and policy scenarios remain labeled; missing OSM heights remain unknown, artificial clouds are identified, and terrain screening uses relative elevations with a datum caveat.

Validation for this revision:

- Seventeen numerical/contract test methods pass, covering geometry defects, greedy capacity assignment, disconnected demand, timestamp order, polygon holes/boundaries, no-wrap shifts, spatial-index boundaries and real-data schemas, alongside the existing core checks.
- All sixteen expanded notebooks execute on desktop with the required WASM kernel. Each produces at least three static graphics and leaves the model trial marked NOT RUN.
- All sixteen execute in JupyterLite/Pyodide through installed Chrome, including rendered-feature checks for the embedded MapLibre scene. Focused reruns cover subsequent numerical and figure-label refinements.
- Five interactive scenes pass standalone and iframe tests: synthetic buildings, real footprints, deck.gl access/trips, synthetic terrain and real terrain. Checks cover filtering, visible/full population totals, active timestamped trips, preserved terrain values and selected cross-section rows.
- JupyterLite builds with the helper modules and bundled data. JupyterBook builds with warnings treated as errors. Static comparison figures, concept maps and scene screenshots were visually inspected; color scales and raster tick labels were refined for readability.

Reports and screenshots remain in ignored `test-results/`. Browser tests use `BROWSER_EXECUTABLE` to select installed Chrome because the local Playwright download has a certificate-chain issue. No live Astra responses, paid API calls, Rust source changes, real-world outcome validation or fully offline deployment tests were performed in this revision. The checks establish executable teaching examples, not measured model capability or operational GIS accuracy.

## Teaching and 3D expansion — October 2, 2026

Reviewed baseline commit `31d70bb`, matching the remote HEAD at the start of this work. The existing numerical examples, explicit synthetic provenance, Rust parity checks and independent notebook execution were useful foundations. The main gaps were short model activities without a complete teaching workflow, one fixed spatial evaluation case, fixed ten-notebook test counts, and no interactive 3D scene beyond Matplotlib massing.

Changes address these gaps with six new labs (11–16), teaching cards in the original ten notebooks, an instructor guide, a strict multi-case grader, three downloadable 3D scenes and manifest-driven checks. Notebook 03's evidence export no longer includes the winning node, so its model-selection task does not reveal the expected answer directly. Candidate scores remain available because that exercise tests selection and interpretation rather than independent routing.

Local checks completed:

- Ten numerical/contract test methods pass, including hand-checked raster masks, disconnected-population denominators, strict JSON grading, independently checked graph paths, and 3D coordinate/height preservation.
- All sixteen notebooks execute on desktop Python 3.13 with schema validation, embedded assertions, static plots and the required Wasmtime kernel.
- All sixteen notebooks also complete in JupyterLite/Pyodide with executed cells, no error outputs and static plots. All three mapping notebooks passed a focused rerun after the iframe fix below, including a rendered-feature check for MapLibre.
- All three HTML scenes render in Chrome with real WebGL canvases. MapLibre height/top-view controls, deck.gl scenario/extrusion controls, and Plotly water/exaggeration controls pass automated checks. Scene screenshots were visually reviewed.
- JupyterLite builds with all sixteen notebooks and shared scene templates. JupyterBook builds with warnings treated as errors, including the teaching chapter and interactive scene outputs.

Reports and screenshots are written to ignored `test-results/`; scene exports are under `test-results/scenes/` and are copied explicitly into `_site/scenes/`. Learner exports are not published wholesale. CI also checks that notebook regeneration produces no committed notebook/manifest drift.

Visual inspection caught a blank MapLibre iframe despite successful Python execution and a working standalone scene. The pinned renderer is affected by [MapLibre issue #7047](https://github.com/maplibre/maplibre-gl-js/issues/7047): direct `about:srcdoc` embeds can fail worker-origin checks. `scene_frame` now navigates a small bootstrap to a same-origin Blob document and revokes the URL after loading. Tests cover both standalone and embedded scenes, and MapLibre readiness requires actual rendered building features rather than initialization alone.

The Playwright browser download was blocked locally by a certificate-chain error. Tests used installed Chrome through `BROWSER_EXECUTABLE`, preserving TLS verification. CI installs its own Chromium normally. Renderer versions are pinned and loaded from their CDNs; no completely offline claim is made.

No actual Astra response was collected during this expansion. Passing fixtures validate the evaluator, not Astra performance. Synthetic scenarios do not validate real-world GIS, hydrology, equity policy, or urban forecasts. Changes are local until committed and published.

## Original release

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
