# Visualization Skills

Two independent Agent Skills for making difficult information easier to understand visually. They produce information structure and suggested ways to represent it, independent of whether the final artifact becomes PlantUML, Mermaid, an ASCII chart, or another medium.

| Skill | Use it for | Deliverable |
| --- | --- | --- |
| [design-visual-explanation](skills/design-visual-explanation/SKILL.md) | Extracting essential meaning, suggesting diagram forms, and planning how to make it visible | Renderer-neutral elements and relationships, with representation suggestions or a full explanation brief |
| [review-visual-explanation](skills/review-visual-explanation/SKILL.md) | Reviewing an existing brief, chart, diagram, or explanatory layout | Material findings and targeted repair suggestions; rewriting only when asked |

Each skill works on its own. Use design for a new brief, review for an existing explanation. Ordinary summaries, formal logic audits, and implementation from an existing specification do not need these skills. Neither skill has external runtime dependencies.

## Install with npx skills

From this checkout:

```bash
npx skills add . --list
npx skills add . --skill design-visual-explanation -a codex -y
npx skills add . --skill review-visual-explanation -a claude-code -y
npx skills add . --skill '*' -a codex -a claude-code -y
```

Add `-g` to explicitly install globally. To install into another project, run the command there and replace `.` with this checkout's absolute path. A published Git repository can be supplied in place of the path. No npm package or plugin manifest is required. See the [skills CLI](https://github.com/vercel-labs/skills).

## Try it

- "Use design-visual-explanation to turn these research notes into a visual brief for our board. Preserve the uncertainties."
- "Use review-visual-explanation to review this diagram against its source. Give only material findings and suggested repairs."
- "Suggest two diagram forms for this material and recommend one. Give the elements and relationships without committing to a rendering syntax."

Supply the material and audience when known. Rendered reviews need an agent that can inspect images or documents. Without source material, the reviewer can assess the artifact but cannot verify its fidelity to the real process or underlying data.

## Repository contents

Git tracks the skills and their runtime references, this README, the license, and ignore rules. Each skill keeps any required references inside its own folder so it can be installed independently.

Evaluation fixtures, source material, research notes, model outputs, galleries, maintenance tooling, and `AGENTS.md` remain local and ignored. They are not required to use either skill.

## Evidence limits

These skills guide design and review; they do not guarantee factual accuracy or improved reader comprehension. Structural validation and model-output checks are different from human comprehension evidence. The latest review composition additions have not had a model evaluation.

## License

[MIT](LICENSE).
