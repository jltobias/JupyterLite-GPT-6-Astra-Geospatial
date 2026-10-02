"""Teaching prompts and acceptance criteria for the original ten notebooks."""

CARDS = {
    '01': ('Audit coordinates', '01_buildings.geojson plus the two coordinate pairs printed above',
           'Identify coordinate order, frame and units. Explain which pair violates the study bounds and why global bounds alone are insufficient.',
           'Add a GeoJSON audit returning feature IDs for unclosed rings, duplicate IDs and points outside the study bounds.',
           'An intentionally reversed coordinate pair fails; unchanged valid features pass; no automatic axis swapping.'),
    '02': ('Challenge an allocation', '02_population.json and the stated allocation assumptions',
           'Distinguish known totals from invented allocation weights. Propose a sensitivity experiment and state which household-level claims cannot be inferred.',
           'Compare population allocation under floor counts of one versus the generated floors. Report the number of people reassigned.',
           'Both allocations sum to 1200; nonresidential buildings get zero; a change in assumptions is not new census evidence.'),
    '03': ('Choose a clinic', '03_access.json; the objective is lowest population-weighted mean travel time',
           'Return the candidate node with the minimum weighted minutes, its score, and one limitation of the walking model. Candidate array index is node ID.',
           'Add a service-threshold sensitivity plot at 10, 15 and 20 minutes for baseline and the chosen additional clinic.',
           'Coverage is nondecreasing with threshold; adding a clinic never increases anyone’s shortest travel time.'),
    '04': ('Explain raster evidence', '04_heat.json and the displayed maps',
           'Compute the population-weighted cooling from the exported baseline and scenario. Explain why this need not equal an area-average change.',
           'Calculate both area-average and population-weighted cooling; expose the sampling method and units in the export.',
           'Zero cooling intensity produces zero change; weighting uses all 1200 residents; raster rows correspond to northing.'),
    '05': ('Audit disconnection', '05_disruption.json and the flood-screening map',
           'Report the fraction of residents disconnected and explain why a finite mean among reachable residents is not a whole-population mean.',
           'Add a sweep over water thresholds while retaining a dry facility. Plot unreachable population separately from reachable-only travel time.',
           'Removing more edges cannot restore reachability; unreachable residents remain in the total population denominator.'),
    '06': ('Review an event contract', '06_events.json and the arbitrary-dose assumptions',
           'Identify which fields establish shared occupancy and which information would still be needed for a disease model. Do not interpret dose as infection probability.',
           'Compare ventilation multipliers 1, 2 and 4 using the same trajectories, then repeat with three fixed seeds.',
           'Within each seed, trajectories are identical across interventions and dose scales inversely with ventilation.'),
    '07': ('Diagnose uncertainty', '07_assimilation.json and the sensor plot',
           'Explain the missing interval and rejected outlier. Distinguish a model uncertainty band from empirically verified interval coverage.',
           'Run the filter on multiple seeded streams and measure empirical interval coverage against synthetic truth.',
           'Missing readings increase prediction variance; changing sensor noise changes gain; report coverage without forcing it to 95%.'),
    '08': ('Audit a learned surrogate', '08_world_model.json, the action range and the rollout plot',
           'Compare one-step error with rollout error, identify action extrapolation, and explain what further evidence a causal policy claim needs.',
           'Compare learned and persistence baselines at horizons 1, 10 and 35 on whole held-out trajectories.',
           'No training/test trajectory overlap; all methods see the same initial states and actions; unsupported actions remain labeled.'),
    '09': ('Measure a model response', '09_prompt.json and optionally 09_map.png only',
           'Follow the JSON schema in the supplied prompt. Use only the supplied evidence; report no invented geographic context.',
           'Add tied-distance and missing-scale cases with explicit tie and abstention rules. Use lab 13 for repeated text-evidence trials.',
           'Malformed responses fail without crashing; ties have a declared policy; fixtures remain clearly separated from model trials.'),
    '10': ('Optimize without changing meaning', 'rust/src/lib.rs and 10_benchmark.json',
           'Propose one optimization, identify its expected crossover costs, and state the parity checks needed before comparing timings.',
           'Benchmark multiple point counts with warm-up and repeated measurements; preserve the arithmetic formula.',
           'Python/NumPy/WASM agree within declared tolerance including zero points; module initialization and call overhead are labeled.'),
}


def teaching_card(number):
    if number not in CARDS:
        return None
    title, evidence, prompt, coding, criteria = CARDS[number]
    return f'''## Teaching lab: {title}
**Before using AI:** write a prediction, run the numerical baseline, and explain one surprising result.

**Astra evidence:** send only {evidence}. Use a fresh conversation and record the exact model,
date, interface, tools and prompt. A task with a supplied result tests interpretation, not independent calculation.

**Copyable Astra prompt:**
> {prompt}

**Copyable Codex task:**
> {coding} Edit the authoring source in `scripts/make_notebooks.py` (or
> `scripts/teaching_labs.py` for labs 11–13), regenerate the notebooks and preserve browser compatibility.
> Use NumPy, Matplotlib and the standard library. Include a small reference case that can be checked by hand.

**Acceptance evidence:** {criteria}

**Share back:** save your original prediction, changed parameter, result, model response and one limitation.
Download the edited notebook and exports. If you have no model access, exchange explanations with a partner
and evaluate them with the same criteria; do not label that activity as an Astra trial.
'''
