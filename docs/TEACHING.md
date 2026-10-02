# Teaching with Astra, Codex and browser geospatial labs

Every learner can run the numerical baselines without a model account. Learners with Astra access can collect model responses; others can critique a partner's explanation or use the explicitly labeled fixtures. Both paths practice the same evidence checks. Only actual, recorded model responses count as model trials.

## Use the implemented investigations

Every notebook now includes a concept map, an executed extension, spatial comparison graphics and an optional scored Astra trial. Read the four concept-map branches (input, method, evidence, limit) before running the code. Ask learners to predict one pattern, point to it on the resulting map, then verify it numerically. Preserve both outputs when changing an assumption.

| Notebook | Implemented investigation | Visual evidence |
|---|---|---|
| 01 | Audit real OSM geometry and four injected defects | Footprint map, area distribution, defect chart |
| 02 | Conserve four neighborhood totals under floor assumptions | Allocation and sensitivity maps |
| 03 | Compare travel modes, opening hours and capacities | Access curves and unserved-population map |
| 04 | Inspect real Sentinel reflectance and an artificial cloud mask | NDVI and categorical SCL maps |
| 05 | Sample flooded road endpoints and midpoints | Disconnection curves and reachable network |
| 06 | Link activity histories to places and shared settings | Place/route map and dose comparisons |
| 07 | Check stale sensors and interval coverage | Sensor map, residual heatmap, coverage distributions |
| 08 | Evaluate nonlinear dynamics on held-out trajectories | Neighborhood effects, rollout errors, action-support diagram |
| 09 | Add ties, missing scale and axis-order challenges | Multi-case map atlas and trial register |
| 10 | Compare batched spatial queries and a finite-radius index | Query map and timing curves |
| 11 | Correct a shifted raster without wrapping | Before/after alignment and detected-change maps |
| 12 | Add facility capacities to siting objectives | Worst-group coverage, assignment lines and unserved map |
| 13 | Evaluate polygon holes and explicit boundaries | Containment diagrams and four-family benchmark |
| 14 | Preserve missing heights in real OSM footprints | Flat footprint scene, floor filter and assumption chart |
| 15 | Follow timestamped trips and filter population | Moving markers, route map and trip timeline |
| 16 | Inspect real terrain with relative elevations | Hillshade, elevation map and selectable cross-section |

The `NN_extension_prompt.json` export contains evidence and requested fields, not the answer key. `NN_extension_map.png` is the corresponding shareable figure. Keep the complete notebook and `NN_extension_trial.json` private during a blind model trial because they contain computed reference answers. Record text-only, image-only and combined conditions separately. A missing model response remains **NOT RUN**, never a synthetic success. Some image-only tasks lack enough information; discussing that limitation is part of the lesson.

## Choose a workshop route

| Session | Sequence | Take-home artifact |
|---|---|---|
| First geospatial lesson, 60 minutes | 01 coordinates → 02 population → 09 one-map evaluation | GeoJSON, conservation check and a scored response |
| Environmental evidence, 75 minutes | 04 heat → 11 raster change → discussion | Paired-valid raster calculation and a limitation statement |
| Access and fairness, 75 minutes | 03 routing → 12 equitable siting → 15 interactive layers | Candidate table, chosen objective and a shareable scene |
| 3D mapping studio, 90 minutes | 14 MapLibre → 15 deck.gl → 16 terrain | Three HTML scenes, static checks and a reviewed Codex change |
| AI evaluation, 75 minutes | 09 practice → 13 reserved-seed suite → peer review | Exact prompts, responses, metadata and per-family results |

Times are teaching estimates, excluding first-time runtime downloads. For a shorter lesson choose one notebook; all notebooks are independent. Preflight the classroom network, CDN access and WebGL on representative devices. Keep the JupyterBook's static plots and tables available as the fallback. A fully air-gapped workshop requires separately vendoring and testing the runtimes and renderer assets.

## A repeatable classroom cycle

1. **Predict:** write down what should happen before running or asking a model.
2. **Calculate:** run the baseline, inspect units, and verify one result by hand.
3. **Ask:** send the designated evidence and task in a fresh model session. Keep answer keys out of the prompt for independent problem-solving trials.
4. **Check:** compare numerical answers to the reference and explanations to the stated assumptions. Record incorrect, missing and malformed answers.
5. **Change:** ask Codex for one bounded modification, review the diff and rerun the acceptance checks.
6. **Share:** download the notebook, evidence, exact response and a brief interpretation, including one remaining limitation.

For a visual trial, provide the exported map or a screenshot and task wording; remove coordinate arrays only when the condition is explicitly image-only. A table-based task and an image-based task test different skills. A screenshot does not provide exact geographic coordinates unless the image itself contains sufficient scale and reference information.

## What each tool contributes

| Tool | Role in these notebooks | Verification |
|---|---|---|
| Astra | Interpret evidence, reason about alternatives, produce structured answers, critique maps | Compare to reference calculations and review unsupported claims |
| Codex | Implement a requested change in the repository and run checks | Review source changes, regenerate notebooks, execute tests |
| NumPy / Python | Reproducible spatial and simulation references | Small hand-computed cases and numerical invariants |
| MapLibre GL JS | Geographic footprints extruded by metre-valued height | GeoJSON axis order, source IDs, physical versus exaggerated height |
| deck.gl | Layered geographic polygons, streets, clinics, picking and scenario controls | Stable data, fixed color scale, explicit thematic extrusion units |
| Plotly.js | Scientific terrain surface with water-plane and exaggeration controls | Vertical datum, cell area and unchanged raw elevations |

Official [Astra documentation](https://developers.openai.com/api/docs/models/gpt-6-astra) and [Codex/code generation guidance](https://developers.openai.com/api/docs/guides/code-generation), checked October 2, 2026, support these general reasoning/coding roles. They do not establish geospatial accuracy. Actual model availability and interface/tool access must be recorded for each trial. The examples do not make model API calls.

## 3D mapping studio

**14 — MapLibre:** start at 1× height, rotate, compare top view, then move to 5×. Inspect the same building in the table. Explain why its real height has not changed. Exported HTML includes the source data and controls; it does not need map tiles.

**15 — deck.gl:** toggle existing/additional clinic and physical/population extrusion independently. Identify which control changes colors and which changes height. Read the raw tooltip and table values. Ask whether a tall thematic column could be mistaken for a real tower.

**16 — Plotly terrain:** compare a low and high water plane, then change only vertical exaggeration. Verify that the cell count is unchanged by exaggeration. Explain why a horizontal plane can include hydraulically isolated low cells and cannot establish a real flood extent.

Each scene has keyboard-operable controls, explanatory labels and a static notebook plot. MapLibre and deck.gl also include HTML data tables; the terrain scene provides numerical area summaries and an exported raster. Perspective views remain inherently less accessible than tables and plan views, so do not make visual inspection the only graded activity.

The generated scenes are downloadable HTML files. They embed their data, including explicitly labeled public-data extracts in the footprint and terrain extensions, but still fetch pinned JavaScript/CSS from CDNs. If notebook trust or an embed policy prevents rendering, open the downloaded HTML directly. Do not copy private location data into a public artifact. No 3D model generation, photogrammetry or real-world terrain accuracy is claimed.

## Model-trial record

Keep the displayed model name, date, interface, tools allowed, elapsed time if measured, exact submitted evidence/prompt, unedited response, scoring rules and score. Notebooks 11–13 export trial JSON; lab 13 also supports an uploaded response file. Download and rename each run before rerunning because the export filename is reused. Fixtures remain labeled `FIXTURE`; never present their scores as measured model performance.

Lab 13 reports all scheduled cases, including missing responses. Its routing cases include disconnected targets; containment declares that boundaries count as inside. A practice seed is not a secret test set. Choose a new seed before the trial, keep the answer key local, and disclose repository/tool access. A model with the repository can read the reference generator; that condition tests code-assisted work rather than unaided reasoning.

Review explanatory claims separately from automatic numeric grading. A passing schema is not a correct result. A correct result on these small cases is not evidence of city-scale reliability. Do not widen tolerances after seeing an answer.

## A small assessment rubric

Score each dimension 0 (missing/incorrect), 1 (partial), or 2 (correct and evidenced):

- **Spatial contract:** coordinate order, CRS/frame, units, IDs and nodata are stated correctly.
- **Numerical evidence:** result agrees with a checked calculation and uses the right denominator.
- **Interpretation:** conclusions stay within the data and distinguish visualization from observation.
- **Reproducibility:** prompt, response, model/tool settings, seed and changed parameters are recorded.
- **Sharing:** artifact opens, attribution remains present, and a non-3D alternative is supplied.

## Maintainer workflow

Edit `scripts/make_notebooks.py`, `scripts/teaching_cards.py`, `scripts/teaching_labs.py` or `scripts/mapping_labs.py`, then regenerate. Shared references live in `content/experiments.py`; 3D export helpers and editable HTML/CSS live in `content/scenes.py` and `content/scene_templates/`.

```sh
python scripts/make_notebooks.py
python scripts/test_core.py
python scripts/check_notebooks.py --require-wasm
python scripts/build_site.py
python scripts/build_book.py
python -m playwright install chromium
python scripts/check_scenes.py
python scripts/browser_check.py
```

The scene tests render all three WebGL views and exercise their controls; notebook checks also execute the Python source. Browser checks must succeed before claiming JupyterLite compatibility. JavaScript errors, a blank canvas or an iframe blocked by the viewer are not a successful 3D demonstration. CI checks generated notebooks for drift and discovers notebook counts from the manifest.
