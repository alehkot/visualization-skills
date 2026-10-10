# Evaluation sources

These sources are kept outside `skills/` so either skill remains independently installable without evaluation dependencies. Curated suites are explicitly allowed by `.gitignore`; generated outputs and older local research remain ignored.

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

`42cbc37` is the pre-close-bar-guidance baseline; choose the appropriate baseline for a later change. The selected revision must be available in the local Git checkout; the preparer does not fetch history or fall back to working-tree skill files. Each bundle records the resolved skill commit and hashes of the skill files, local case manifest, and preparer. Cases/tooling come from the current checkout, not the selected skill revision. An existing bundle is never overwritten: use a new output filename for another run. Repository output is restricted to the ignored results directory; an external directory is also allowed.

The JSON `cases` array contains `id` and `model_prompt`. Submit only that prompt in a fresh model context. The separate `rubric` object contains the review instructions and case criteria. No provider integration, credentials, paid API calls, or automatic semantic grading are included. Preserve the raw responses and per-criterion judgments alongside the bundle; do not quietly replace old runs.

For the synthetic rendering suite, install the pinned optional packages in a virtual environment, then run:

```sh
python3 -m pip install -r evaluation/close-bars/requirements-render.txt
python3 evaluation/close-bars/render_fixtures.py --output-dir evaluation/close-bars/results/rendered
```

On restricted machines with a read-only home directory, point `MPLCONFIGDIR` and `XDG_CACHE_HOME` to writable temporary directories before running rendering tests. Matplotlib may maintain its normal cache separately from fixture outputs.

The render command fails clearly when required packages are unavailable. A successful run reports eight `PASS` fixtures and nine `EXPECTED_FAILURE_DETECTED` controls, writes PNGs plus `source_data.json` and `validation_results.json`, and returns zero only when every expected outcome is met. Inspect the PNGs at their actual 640 px and 360 px widths. Rendering does not run or grade a model.

### Interpreting render results

Rendered examples use explicit synthetic source data. A passing run must accept all intended-good fixtures and detect the specified failure in every deliberately broken control. A failure control may have additional defects; the named expected failure must still be detected. Numeric and renderer-object assertions should be supplemented with actual PNG inspection at the exported size. Labels that fit geometrically are not thereby proven easy for every reader to understand.

Keep arithmetic/render checks distinct from model scores. Never report “the model passed” merely because a Python test or a hand-authored chart passed.
