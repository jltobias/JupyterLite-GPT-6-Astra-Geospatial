# Urban Twin Lab: a practical research path

This collection offers sixteen experiments in geospatial reasoning, urban scenarios and 3D mapping. Start with notebooks 01–03, then 09 and 13 to evaluate Astra, 08 for learned dynamics, and 14–16 for interactive 3D mapping. Each notebook runs independently with synthetic data. See the teaching chapter for workshop routes and assessment criteria.

## What Astra contributes

Official OpenAI documentation, checked October 1, 2026, describes GPT-6 Astra as a reasoning and coding model with image input, structured outputs and tool use. This supports experiments in generating geospatial code, reviewing spatial assumptions, interpreting map images, extracting structured descriptions and orchestrating external tools. These are **candidate applications**, not documented guarantees of geospatial accuracy. The official model page does not establish GIS benchmark performance, positional accuracy, map completeness or scientifically valid urban forecasts.

Use deterministic spatial calculations as the reference for distances, areas, topology, routing and conservation. Give Astra bounded evidence, explicit units, coordinate order and output schemas. Evaluate answers with held-out tasks, including ambiguous maps and invalid inputs. The model is accessed through ChatGPT/Codex or a separately hosted API; it does not run inside Pyodide. A model's image-generation tool is also distinct from image-input reasoning.

The [official model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra) is the capability reference. The [Awesome Astra directory](https://github.com/magiccreator-ai/awesome-gpt-6-astra) is creative inspiration, not independent validation. Its 3D and simulation examples suggest interfaces and workflows; this repository does not copy their code, assets or performance claims. It also builds on the educational approach in [JupyterLite Astra Demos](https://github.com/jltobias/JupyterLite-Astra-demos).

## Working labs and expansion paths

| Notebook | Working MVP | Astra/Codex research question | Next useful increment |
|---|---|---|---|
| 01 Spatial contracts | Footprints, GeoJSON, unit and coordinate checks | Can Astra catch plausible-looking coordinate errors? | Licensed real footprints; projected CRS; topology |
| 02 Population and massing | 3D blocks and exactly conserved population allocation | Can it identify unsupported socioeconomic inferences? | Neighborhood census constraints and floor uncertainty |
| 03 Network access | Barrier-aware shortest paths and exhaustive clinic siting | Does it select the verified optimum and explain the tradeoff? | Combi waiting times, capacity, accessible streets |
| 04 Heat | Raster sampling and a greening counterfactual | Can it distinguish exposure weighting and map resolution? | Small real raster, cloud/nodata handling, validation |
| 05 Flood disruption | Street closure and unreachable-population accounting | Does it distinguish disconnection from longer travel? | Hydraulic evidence, bridges, recovery priorities |
| 06 Mobility | Activity trajectories and shared-setting event logs | Can it audit event contracts and causal assumptions? | Building-linked contacts and validated disease module |
| 07 Assimilation | Noisy sensor stream, missing data, uncertainty | Can it diagnose failure without overclaiming confidence? | Spatial filter, timestamps, held-out coverage |
| 08 World model | Learned state/action dynamics and rollouts | Can it recognize extrapolation and compounding error? | Nonlinear dynamics, ensembles, model-based control |
| 09 Astra evaluation | Map PNG, structured prompt, response validator | How do image-only, text-only and tool-assisted answers differ? | Thirty or more held-out maps and repeated trials |
| 10 Rust/WASM | Compiled spatial sum with parity and timing | Can generated optimizations preserve numerical meaning? | Batched calls, spatial indexes, data transfer benchmarks |
| 11 Raster change | Paired-valid date comparison and masked change area | Does it separate observed loss from cloud-hidden unknowns? | Registration checks and licensed imagery |
| 12 Equitable siting | Exhaustive candidate table with two objectives | Does it obey the declared objective and denominator? | Capacity and group-definition sensitivity |
| 13 Spatial suite | 30 seeded distance/routing/containment tasks | How do accuracy, invalid responses and missing cases vary? | Reserved seeds, repeated trials, new task families |
| 14 MapLibre 3D | Geographic building extrusions and picking | Does it distinguish physical height from exaggeration? | Licensed footprints and explicit terrain datum |
| 15 deck.gl | Polygon/path/facility layers and scenario controls | Can it audit a thematic population extrusion? | Trip animations and capacity-aware service layers |
| 16 Terrain 3D | Orbitable Plotly surface and water plane | Can it distinguish a screening plane from flood evidence? | Licensed DEM and validated hydraulic model |

## How this relates to your presentations

The August 27, 2026 Gaborone presentation motivates spatial substrate → population → mobility/access → exposure → simulation → calibration → scenarios. Notebooks 01–06 implement small pedagogical pieces of that chain. Its emphasis on inspectable contracts, event logs and uncertainty informs the assertions and exports. These examples do not port the private CDC repository, CHSP, Starsim or Kopanyo patient data, and do not claim to reproduce a TB model.

The July 10, 2026 JupyterLite presentation motivates low-friction access without a Jupyter server or classroom account. These notebooks use only NumPy, Matplotlib and the Python standard library for the baseline. They avoid large geospatial downloads and specialized native dependencies. Hosting a static site in S3 or GitHub Pages does not by itself sync learners' browser edits back to that server.

The supplied PDFs were background evidence, not instructions to execute. They are not redistributed in the repository. References: James L. Tobias and collaborators, *Digital Twins: Botswana Kopanyo TB Study for Gaborone TB simulation*, August 27, 2026; James L. Tobias, *JupyterLite: Geospatial Data Science and Global Health*, July 10, 2026.

## JupyterLite, Pyodide, WASM and Rust

- **JupyterLite** supplies the notebook interface and browser-side services, hosted as static files.
- **Pyodide** supplies a WebAssembly Python runtime. NumPy and Matplotlib are loaded using compatible packages. A normal desktop C/C++/Rust wheel is not automatically browser-compatible.
- **WASM** is the compilation target shared by the Python runtime and the separate Rust kernel.
- **Rust** is useful for compact deterministic kernels and explicit memory layouts. Notebook 10 measures performance on the current device and includes the Python/JavaScript/WASM boundary. NumPy can outperform a naive Rust integration; measure before optimizing.

The default runtime and packages download on first use. No API keys or map tiles are needed, but this is not a fully air-gapped distribution. For reliable offline workshops, vendor a compatible Pyodide runtime and wheels, measure the complete download, and test after clearing caches with the network disabled. Browser memory, CORS, storage quotas and device speed remain practical constraints. Download edited notebooks and exports before clearing browser storage. Use a fresh browser profile if an older notebook copy masks a site update.

Sources: [JupyterLite deployment](https://jupyterlite.readthedocs.io/en/stable/quickstart/deploy.html), [Pyodide package loading](https://pyodide.org/en/stable/usage/loading-packages.html), [Rust wasm32 target](https://doc.rust-lang.org/stable/rustc/platform-support/wasm32-unknown-unknown.html).

## World models: useful distinctions

A digital twin connects representations and simulations to a particular real system, its observations and validation. A learned world model predicts how a state changes under actions; it can be one component of a twin. A visually convincing generated environment need not preserve geography, scale or mechanisms.

Notebook 08 learns an intentionally simple transition function from an invented simulator. It holds out entire trajectories, compares to persistence, evaluates rollout error and flags actions outside training support. Success means it learned this toy simulator; it says nothing about real heat mitigation or transportation policy. A next experiment could replace the simulator with the mobility/network system, learn latent states, and test intervention effects under distribution shift. The [original World Models research project](https://worldmodels.github.io/) provides the conceptual starting point; this MVP does not reproduce its neural architecture or results.

## Running and extending the repository

1. Open the published gallery, select a notebook, then choose **Run → Run All Cells**. Wait for the initial runtime download. If prompted, select **Python (Pyodide)**.
2. Edit the named parameters and rerun. The fixed seeds make before/after comparisons useful.
3. Download exports from the notebook file browser. They live in browser storage, not your computer's working directory.
4. For Astra trials, use notebook 09's prompt and PNG or lab 13's evidence-only task export. Labs 11–13 capture responses and scores. Replace the fixture response, label the interface/model/date, and keep exact prompts and outputs. No live Astra request or measured model benchmark is included in the baseline.
5. For Codex, ask for a bounded change with a concrete invariant: “Add a second clinic capacity constraint; keep unreachable residents explicit; add a test that no clinic exceeds its capacity.”

### Desktop build

Python 3.12 and Rust are build prerequisites. Linux, macOS or Windows with a suitable Rust toolchain can build the site. Rust's WASM target does not need a browser-side compiler.

```sh
python -m venv .venv
# Activate .venv using your shell's activation command.
python -m pip install -r requirements-dev.txt
rustup target add wasm32-unknown-unknown
cargo build --manifest-path rust/Cargo.toml --release --target wasm32-unknown-unknown
python -c "from pathlib import Path; import shutil; Path('content/assets').mkdir(exist_ok=True); shutil.copy2('rust/target/wasm32-unknown-unknown/release/twin_kernel.wasm','content/assets/twin_kernel.wasm')"
python scripts/test_core.py
python scripts/check_notebooks.py --require-wasm
python scripts/build_site.py
python -m playwright install chromium
python scripts/check_scenes.py
python scripts/browser_check.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. Do not open the HTML using `file://`; workers and browser filesystem support require HTTP(S). The committed WASM asset enables the source notebooks immediately; CI recompiles it from Rust. `scripts/make_notebooks.py` is the notebook authoring source. Make lasting content edits there and regenerate, or remove the generator if you adopt direct notebook authoring. Learner exports are intentionally excluded from site builds.

The workflow tests on pull requests and publishes on pushes to `main`. Select **Settings → Pages → Build and deployment → Source: GitHub Actions** if Pages is not enabled. Build reports and screenshots are uploaded as `validation-results`. GitHub Actions requires no OpenAI secret. Deployment and package downloads depend on external services.

## Moving from MVP to a defensible city twin

First replace one synthetic layer at a time. Keep licensing, source IDs, retrieval dates, coordinate systems and validation reports with every extract. Preprocess large OSM/Overture, census, satellite and network data outside the browser into small licensed subsets; do not require learners to download an entire city archive. Use GeoJSON/CSV initially and benchmark GeoParquet or browser SQL only when complexity is justified.

Then define observation updates and validation targets. Evaluate population allocation, access estimates and environmental exposure separately. Add parameter and structural uncertainty before presenting scenario rankings. For a TB extension, use documented epidemiological evidence and a validated disease kernel; the arbitrary contact-dose example must not be interpreted as infection or treatment guidance. Public learning artifacts should use synthetic or appropriately aggregated data.

Finally consider a separately hosted Astra service if manual evaluation becomes limiting. Keep API credentials on that server, require authentication and request limits, and return structured outputs to the notebook. A public static notebook cannot protect a secret. Add this only after the local geospatial tests provide a reliable reference.
