# Evaluation sources

These sources are kept outside `skills/` so either skill remains independently installable without evaluation dependencies. Curated suites are explicitly allowed by `.gitignore`; generated outputs and older local research remain ignored.

All quantitative suites use the single [prompt preparer](close-bars/prepare_eval.py). Select a suite with `--cases`; its case manifest and rubrics remain separate. Case IDs are local to a suite: record `close-bars/P1` or `missing-data/P1` or `mix-effects/P1`, not an ambiguous `P1` when combining results.

## Close-bar comparisons

The [case manifest and rubrics](close-bars/cases.json) cover the close-bar failure modes and legitimate counterexamples. Several cases deliberately resemble the skill's worked examples; these are regression/smoke probes, not held-out generalization evidence.

The suite separates three kinds of evidence:

| Check | What it tests | What it does not establish |
| --- | --- | --- |
| Versioned model tasks and rubrics | How a model applies a specified skill revision to source-backed design/review tasks | Deterministic model output, general reliability, or reader comprehension |
| Standard-library unit tests | Input validation, prompt provenance, arithmetic and detection helpers | Whether a model follows the skill |
| Synthetic rendered fixtures | Label/source agreement, geometry, spacing and deliberate rendering failures at two sizes | Skill-generated output quality, statistical validity or accessibility conformance |

Generated bundles, model responses, scores, PNGs and reports belong under `close-bars/results/` (ignored), or a separate directory outside the repository. Do not add them to an installable skill folder.

### Model evaluation protocol

Prepare the same cases for a baseline and candidate revision. Send only each task's model-facing prompt to the model, not the grading rubric. Keep cases separate, use the same model/settings and tool access for both revisions, and retain raw answers before grading.

A reviewer should grade each answer against the case's acceptance and material-failure criteria, recording pass/fail, short evidence from the answer, and any ambiguous or unassessable criterion. Equivalent task-faithful wording and forms are acceptable; do not grade by keyword matching. An absent rendered artifact cannot establish actual clipping or legibility.

Record the bundle's resolved commit and content hashes, model/version if available, settings, tool access, run time, raw answer, and reviewer judgment. For comparison, report every case and both denominators rather than selecting favorable examples. Use repeated runs and blinded grading when estimating reliability; a single run is only a smoke check.

The preparer supplies the selected skill entrypoint and quantitative reference inline. It therefore evaluates application of those instructions, not whether an agent autonomously discovers the right reference. The hashes identify the inputs, not a promise that a provider can replay identical outputs.

### Continuous integration

[Evaluation regressions](../.github/workflows/evaluations.yml) runs on every push and pull request using Python 3.12 on Ubuntu, with the existing pinned optional renderer installed. It invokes all three suite directories explicitly: root-level unittest discovery does not find these tests. It also runs the full rendering CLI, which fails when renderer dependencies are unavailable rather than silently accepting skipped rendering tests.

The job runs the same checks documented below. It does not run a model, grade written responses, install a skill in a separate agent, or establish reader comprehension. The gallery is generated in the runner's temporary directory; reproduce it locally to inspect the PNGs. Actions are pinned to full commit hashes, the token is read-only, checkout credentials are not persisted, and the job has a ten-minute timeout. No credentials or paid model service are required. This workflow does not configure branch protection or make itself a required check.

### Commands

Run from the repository root. The preparer and non-rendering tests use Python's standard library and Git. The suite was tested with Python 3.12; rendering dependencies are optional and separate from the skills.

Run the harness/helper tests:

```sh
python3 -m unittest discover -s evaluation/close-bars -p 'test_*.py' -v
```

Renderer-specific tests may skip when optional packages are absent. Inspect the reported skips; a skipped render test is not a pass. To run only the standard-library prompt-preparation tests:

```sh
python3 -m unittest discover -s evaluation/close-bars -p 'test_semantic.py' -v
```

Prepare a baseline and candidate, keeping the same local case manifest for both:

```sh
python3 evaluation/close-bars/prepare_eval.py --revision 42cbc37 --output evaluation/close-bars/results/baseline.json
python3 evaluation/close-bars/prepare_eval.py --revision HEAD --output evaluation/close-bars/results/candidate.json
```

`42cbc37` is the pre-close-bar-guidance baseline; choose the appropriate baseline for a later change. The selected revision must be available in the local Git checkout; the preparer does not fetch history or fall back to working-tree skill files. Each bundle records the resolved skill commit and hashes of the skill files, local case manifest, and preparer. Cases/tooling come from the current checkout, not the selected skill revision. An existing bundle is never overwritten: use a new output filename for another run. Repository output is restricted to the explicitly allowed, Git-ignored `evaluation/close-bars/results/`, `evaluation/missing-data/results/`, and `evaluation/mix-effects/results/` directories; an external directory is also allowed. Merely ignoring another repository directory does not allow output there.

The JSON `cases` array contains `id` and `model_prompt`. Submit only that prompt in a fresh model context. The separate `rubric` object contains the review instructions and case criteria. No provider integration, credentials, paid API calls, or automatic semantic grading are included. Preserve the raw responses and per-criterion judgments alongside the bundle; do not quietly replace old runs.

For the synthetic rendering suite, install the pinned optional packages in a virtual environment, then run:

```sh
python3 -m pip install -r evaluation/close-bars/requirements-render.txt
python3 evaluation/close-bars/render_fixtures.py --output-dir evaluation/close-bars/results/rendered
```

On restricted machines with a read-only home directory, point `MPLCONFIGDIR` and `XDG_CACHE_HOME` to writable temporary directories before running rendering tests. Matplotlib may maintain its normal cache separately from fixture outputs.

The render command fails clearly when required packages are unavailable. A successful run reports eight `PASS` fixtures and eleven `EXPECTED_FAILURE_DETECTED` controls, writes PNGs plus `source_data.json` and `validation_results.json`, and returns zero only when every expected outcome is met. Inspect the PNGs at their actual 640 px and 360 px widths. Rendering does not run or grade a model.

Rerunning a gallery directory replaces its generated artifacts. Once rendering dependencies and the output directory are accepted, the previous `validation_results.json` is removed **before** any source/PNG output is changed. A new report appears only after all fixtures finish and its complete JSON has been written to a sibling temporary file. An interrupted or failed generation can leave partial or mixed artifacts without a report; do not treat those files as a completed evaluation. Rerun successfully or use a fresh directory. Invalid output paths or unavailable renderer dependencies leave the previous gallery untouched.

This protects report publication, not the entire gallery as a transaction: use a distinct output directory for each concurrent run or for evidence you need to retain. Abrupt process termination can leave a `.validation-results-*.tmp` file; it is not a completed report. A complete report can contain failed checks, so inspect statuses and the command's exit code rather than treating report existence as success.

### Interpreting render results

Rendered examples use explicit synthetic source data. A passing run must accept all intended-good fixtures and detect the specified failure in every deliberately broken control. A failure control may have additional defects; the named expected failure must still be detected. Numeric and renderer-object assertions should be supplemented with actual PNG inspection at the exported size. Labels that fit geometrically are not thereby proven easy for every reader to understand.

The numeric-axis audit compares actually visible tick text with its numeric location, including visible labels on either side and labeled minor ticks. It catches wrong magnitude/sign/units, displaced label anchors, rectangular clipping, missing major labels, and hidden axes; out-of-view ticks are excluded. These fixture axes require at least two distinct in-view major ticks, but do not prescribe their original spacing or the number of printed decimals. The negative and elapsed-time fixtures may inherit units from their visible captions. Custom formatters are accepted when they produce a complete plain numeric label in the fixture's units (including Unicode minus or `e` notation).

This is deliberately a check of these synthetic linear axes, not a general formatter interpreter: separate scientific multipliers/additive offsets, nonlinear scales, math-text numbers, locale-specific number syntax, and arbitrary tick-label clip paths report unsupported/invalid checks rather than receiving a pass. The new factor-ten tick-label control keeps the bars unchanged while corrupting the visible scale.

The uncertainty audit inspects actual `ErrorbarContainer` children in the positive and negative fixtures. Each source interval requires one solid stem and two perpendicular caps attached to the expected axes. Transformed stem endpoints and cap centers must agree with the independent synthetic source and the associated bar center (within 0.1 display pixels); container order is irrelevant. Missing, hidden, detached, transparent, zero-width/zero-size, displaced, clipped, duplicated, or source-inconsistent components fail. Collision bounds now come from the actual stem and cap strokes, including marker size and edge width, intersected with rectangular clipping and the canvas. Removing whiskers therefore cannot leave phantom source-derived collision rectangles. The added `positive_bad_missing_uncertainty` control removes every whisker while preserving the healthy labels.

This is a deliberately narrow artist audit for these fixtures under the pinned Matplotlib renderer. It supports equivalent affine transforms, ordinary positive stroke widths and cap sizes, nontransparent colors, and containing or disabled rectangular clips. Nonzero collection offsets, multiple/empty segments, nonstandard cap markers or marker transforms, marker subsampling, dashes, arbitrary clip paths, animated artists, path effects, sketching, and raster filters report unsupported checks. The full cap `MarkerStyle` is read through Matplotlib's private `_marker` field because its public marker-name getter omits custom transforms; revisit that check when changing the renderer pin. Unregistered line collections are rejected in these two fixtures. This is not a general plot/artist discovery mechanism.

Deterministic mutations cover disappearance, source/geometry corruption, actual versus phantom collisions, unsupported effects, and both orientations. Positive controls preserve healthy fixtures at both widths, reordered containers, equivalent transforms, and ordinary style/clip variations. Stroke bounding boxes are conservative; they do not prove pixel-level coverage, contrast, absence of occlusion, statistical validity, or reader comprehension. These checks do not validate arbitrary uncertainty graphics or infer whether a claimed confidence interval is statistically justified.

Keep arithmetic/render checks distinct from model scores. Never report “the model passed” merely because a Python test or a hand-authored chart passed.

## Missing observations, zeros, and estimates

The [missing-data case manifest and rubrics](missing-data/cases.json) contain ten targeted written probes, evenly split between design and review. They cover:

- Explicit missing readings versus observed zero, including isolated observations that a line-only display could lose
- Scheduled dates absent from exported rows
- Missing bars visually indistinguishable from zero without sufficient status information
- Legitimate irregular sampling, unknown cadence, and labeled connectors as controls against overcorrection
- Source-supplied estimates with their measured/estimated distinction preserved
- An adequate associated status table that does not need duplicate labels
- Unknown missingness reasons that do not establish an outage or cause
- A required monthly average whose missing day cannot silently become zero or change the denominator

These are targeted regression/smoke probes informed by the guidance, not held-out generalization evidence. Review source-faithful outcomes rather than requiring every gap to be broken, a universal chart form, an API, or invented inference. The suite has no model runner, keyword-based semantic grader, or missing-data renderer. Its standard-library tests validate the authored manifest, shared preparer, hashes, rubric separation, and output safeguards; passing them is not evidence of model improvement.

### Prepare the same missing-data tasks for both revisions

Run from the repository root. `be6de0f` is the pre-missing-data-guidance baseline. Commit the candidate skill edits before using `HEAD`, or replace it with another available committed revision. The preparer never reads uncommitted skill edits.

```sh
python3 evaluation/close-bars/prepare_eval.py --revision be6de0f --cases evaluation/missing-data/cases.json --output evaluation/missing-data/results/baseline.json
python3 evaluation/close-bars/prepare_eval.py --revision HEAD --cases evaluation/missing-data/cases.json --output evaluation/missing-data/results/candidate.json
```

Both commands must use the same unchanged local case manifest and preparer. Verify that `provenance.cases_sha256` and `provenance.preparer_sha256` match across bundles; retain each bundle's resolved skill commit and per-file hashes. Do not fetch cases independently from each skill revision, quietly replace an old bundle, or compare unlike task sets. Use fresh filenames for additional runs.

Follow the model-evaluation protocol above: submit only one `model_prompt` per fresh context, keep rubrics private from the model, hold model/settings/tool access fixed, and retain raw responses before manual grading. The missing-data tasks permit up to 160 words; the close-bar tasks permit 120. Report every paired case, the design/review breakdown, both denominators, and unclear judgments. A single run is a smoke check; these brief-only tasks cannot establish actual rendering behavior, readability, accessibility conformance, or reader comprehension. Inline references also do not test autonomous reference selection.

### Run all checks

```sh
python3 -m unittest discover -s evaluation/close-bars -p 'test_*.py' -v
python3 -m unittest discover -s evaluation/missing-data -p 'test_*.py' -v
python3 -m unittest discover -s evaluation/mix-effects -p 'test_*.py' -v
```

The first command includes optional close-bar rendering checks; inspect skips as described above. For standard-library-only checks, replace its pattern with `test_semantic.py`. The missing-data suite requires only Python's standard library and Git. Generated bundles, responses, scores, and reports belong in its ignored `results/` directory or outside the repository, never in either installable skill.


## Aggregation and mix effects

The [mix-effects manifest and rubrics](mix-effects/cases.json) exercise existing quantitative guidance on subgroup composition, weighting, and task-dependent comparisons. The ten written cases are split evenly between design and review. They distinguish an aggregate rate from subgroup rates, actual counts from a source-specified standardized comparison, and incomplete or overlapping groups from an exhaustive partition. Controls preserve valid aggregate-only summaries rather than requiring every chart to be disaggregated.

For example, both request types can improve while the overall completion rate falls as the request mix changes. Replacing the observed overall rate with an unweighted average of the subgroup rates is not a valid repair. These tasks ask for source-faithful explanation, not a universal chart type, causal diagnosis, or invented counterfactual adjustment.

[Armstrong and Wattenberg, Visualizing Statistical Mix Effects and Simpson's Paradox](https://research.google/pubs/visualizing-statistical-mix-effects-and-simpsons-paradox/) (IEEE InfoVis 2014) motivates explicitly inspecting mixture effects in aggregated visualizations. The tasks and numbers here are original synthetic fixtures. The paper does not validate this suite, and its proposed comet chart is not required by these rubrics. The separation between executable checks and task/readability evidence also follows the distinction made by [VisEval](https://github.com/microsoft/VisEval); this repository does not add that toolkit as a dependency.

Prepare inputs using the same local manifest and preparer for each committed skill revision:

```sh
python3 evaluation/close-bars/prepare_eval.py --revision HEAD --cases evaluation/mix-effects/cases.json --output evaluation/mix-effects/results/inputs.json
python3 -m unittest discover -s evaluation/mix-effects -p 'test_*.py' -v
```

Choose explicit baseline and candidate revisions when comparing a later skill change, and use new output names. This suite adds no skill change and establishes no before/after model gain. Follow the fresh-context, rubric-withholding and raw-response retention protocol above. Tasks permit 160 words. No model is run or scored by the tests or CI: they check the manifest, its arithmetic fixtures, provenance, rubric separation, and output protections. The tasks are targeted smoke/regression probes, not held-out generalization, rendered-output, causal-inference, or human-comprehension evidence.
