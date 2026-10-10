# Visualization Skills

Two independent Agent Skills for making difficult information easier to understand visually. They produce information structure and suggested ways to represent it, independent of whether the final artifact becomes PlantUML, Mermaid, an ASCII chart, or another medium.

| Skill | Use it for | Deliverable |
| --- | --- | --- |
| [design-visual-explanation](skills/design-visual-explanation/SKILL.md) | Extracting essential meaning, suggesting diagram forms, and planning how to make it visible | Renderer-neutral elements and relationships, with representation suggestions or a full explanation brief |
| [review-visual-explanation](skills/review-visual-explanation/SKILL.md) | Reviewing an existing brief, chart, diagram, or explanatory layout | Material findings and targeted repair suggestions; rewriting only when asked |

Each skill works on its own. Use design for a new brief, review for an existing explanation. Ordinary summaries, formal logic audits, and implementation from an existing specification do not need these skills. Neither skill has external runtime dependencies.

## Guidance and references

Each entrypoint links to focused references with explicit loading conditions. Agents read the detail needed for the current task; a simple request does not require the entire collection. References contain decision procedures, original worked examples and counterexamples, and annotated sources with their limits.

| Topic | Design guidance | Review guidance |
| --- | --- | --- |
| Reader task and representation | [Choose forms by the inference they support](skills/design-visual-explanation/references/task-and-representation.md) | [Distinguish established problems from preferences](skills/review-visual-explanation/references/evidence-and-judgment.md) |
| Systems and relationships | [Preserve conditions, states, membership, and feedback](skills/design-visual-explanation/references/systems-and-relationships.md) | [Trace and countercheck the asserted model](skills/review-visual-explanation/references/systems-and-relationships.md) |
| Quantities and uncertainty | [Define comparisons, conditional percentages, and encodings](skills/design-visual-explanation/references/quantitative-explanations.md) | [Check values, reference groups, scales, and inferences](skills/review-visual-explanation/references/quantitative-review.md) |
| Composition and multiple views | [Arrange evidence around the reader's task](skills/design-visual-explanation/references/composition-and-multiple-views.md) | [Locate reading obstacles and lost correspondence](skills/review-visual-explanation/references/composition-and-multiple-views.md) |
| Explanatory illustration | [Choose views and disclose transformations](skills/design-visual-explanation/references/explanatory-illustration.md) | [Separate physical claims from drawing conventions](skills/review-visual-explanation/references/illustration-review.md) |
| Accessibility and delivery | [Preserve meaning across requested surfaces](skills/design-visual-explanation/references/accessibility-and-delivery.md) | [Check alternative access and supplied variants](skills/review-visual-explanation/references/accessibility-and-variants.md) |

The organization takes inspiration from [Impeccable](https://github.com/pbakaus/impeccable). The guidance and teaching examples are written for visual explanation; source links distinguish research findings, frameworks, practitioner advice, and local applications. Sources are attribution and further reading, not runtime dependencies or evidence that these skills improve comprehension.

## Install with npx skills

Run this from your project's directory to choose skills and agents interactively:

```bash
npx skills add alehkot/visualization-skills
```

To list available skills or select them explicitly:

```bash
npx skills add alehkot/visualization-skills --list
npx skills add alehkot/visualization-skills --skill design-visual-explanation -a codex -y
npx skills add alehkot/visualization-skills --skill review-visual-explanation -a claude-code -y
npx skills add alehkot/visualization-skills --skill '*' -a codex -a claude-code -y
```

Add `-g` to install globally instead of into the current project. For a local checkout, replace `alehkot/visualization-skills` with its path (`.` when running inside it). No npm package or plugin manifest is required. See the [skills CLI](https://github.com/vercel-labs/skills).

## Try it

- "Use design-visual-explanation to turn these research notes into a visual brief for our board. Preserve the uncertainties."
- "Use review-visual-explanation to review this diagram against its source. Give only material findings and suggested repairs."
- "Suggest two diagram forms for this material and recommend one. Give the elements and relationships without committing to a rendering syntax."

Supply the material and audience when known. Rendered reviews need an agent that can inspect images or documents. Without source material, the reviewer can assess the artifact but cannot verify its fidelity to the real process or underlying data.

## Repository contents

Git tracks the skills and their runtime references, this README, the license, ignore rules, and curated [evaluation sources](evaluation/README.md). Each skill keeps any required references inside its own folder so it can be installed independently; evaluation tooling is outside the installable skill folders.

The close-bar evaluation suite includes replayable model prompts and rubrics, plus separate deterministic rendering checks. Generated outputs, galleries, historical local evaluations, research notes, and `AGENTS.md` remain ignored. None are required to use either skill.

## Evidence limits

The [close-bar evaluation suite](evaluation/README.md) makes its inputs and checks reproducible. Preparing prompts or passing arithmetic/rendering fixtures does not establish model compliance or improved reader comprehension; model responses need separate rubric-based review.

These skills guide design and review; they do not guarantee factual accuracy or improved reader comprehension. Structural validation and model-output checks are different from human comprehension evidence.

A local five-problem with-skill/without-skill model comparison covered the expanded design skill at `152108e`, with all six references supplied inline. It does not establish a general benefit or test conditional reference loading. That comparison did not evaluate the expanded review skill or later instruction changes.

A local ten-problem text-only smoke comparison of `ea0cb4a` and the conditional-percentage guidance used one separately prompted model run per version, with both skills exercised. Both versions met all ten hand-checked semantic criteria, so it detected no regression and no demonstrated performance improvement. It did not assess rendered artifacts, general reference-loading reliability, or reader comprehension. Neither skill has had a human comprehension study.

## License

[MIT](LICENSE).
