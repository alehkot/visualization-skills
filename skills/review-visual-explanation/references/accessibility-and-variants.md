# Accessibility and delivery variants

Use this reference when reviewing non-color meaning, text alternatives, interactive access, or supplied versions such as print, monochrome, and narrow layouts. Review the actual surface and requested scope; do not certify implementations that were not inspected.

## State the inspection boundary

Identify whether the evidence is a brief, image, PDF, live interface, or a collection of variants. A screenshot can reveal visible color dependence or clipping. It does not reveal the accessibility tree, keyboard behavior, hidden description, or export settings.

A brief can specify an inadequate alternative or omit an expressly required print condition. It cannot prove that future text is too small or that a particular screen reader will announce it incorrectly. Keep missing implementation evidence separate from an established defect in the specified content.

Use the user's intended task to identify essential information: exact values, distinctions, relationships, conclusions, or exceptions. Different routes to that information can be legitimate. Do not insist on identical visual layouts across formats.

## Check alternative access to meaning

| Inspect | Evidence of a problem | Countercheck before reporting |
| --- | --- | --- |
| Color-coded meaning | A required distinction is recoverable only from hue in the inspected artifact. | Do direct labels, patterns, position, or associated text already distinguish it? |
| Text alternative | Supplied description omits a relationship, value, or qualification necessary for the task. | Does associated accessible content supply it? Is the task summary or exact lookup? |
| Reading sequence | Supplied order separates a condition from its claim or changes the apparent relationship. | Do headings, labels, or an explicit cross-reference preserve the meaning? |
| Static version | A needed hover detail, animation state, or exception is absent. | Is it included in the actual print caption, table, or another supplied part of the artifact? |
| Narrow version | Inspected reflow clips required content or loses correspondence. | Is the missing information available through the provided interaction or accompanying content? |
| Interaction | A necessary operation fails using a tested input method. | Was the actual control and relevant state tested, rather than inferred from an image? |

Adding an unexplained icon is not automatically a fix for color dependence. The replacement cue must carry the distinction. Conversely, a color-rich figure with adequate labels is not defective merely because hue contributes to its appearance.

For a numerical contrast finding, use the actual relevant colors and the applicable criterion, including its conditions and exceptions. Do not estimate a contrast ratio by looking at a screenshot. When exact measurement is unavailable, describe the visible concern at the inspected scale without presenting a formal conformance result.

## Review text alternatives for the same task

Read the supplied alternative independently. Does it preserve the intended conclusion, supporting relationships, uncertainty, and relevant source scope? “A chart with blue bars” identifies appearance but may omit the information the chart exists to convey.

A table may provide all values yet omit a causal mechanism. A concise summary may communicate the trend yet fail an exact-value lookup task. Recommend the missing information or structure, not a fixed description length. Do not add stronger claims than the visual or source supports.

Repeated information is not always harmful. A concise identifier can point to a fuller explanation, and directly associated prose can remove the need for duplicating a long description. Check the supplied association where the medium permits inspection.

## Worked example: a static category key

An invented classification chart assigns observations to **measured**, **estimated**, or **not available**. Its complete written specification says that the downloadable static image contains only unlabeled colored dots; category names appear solely in hover tooltips in the interactive version.

For the requested static download, the category meanings are missing. A minimal repair is to add direct category labels or a clear non-color key, retaining “not available” as distinct from an estimate or zero. The interactive version's tooltips do not supply information to the static image.

A control specification includes category words next to each dot in the static output. Do not report color-only meaning on that version. Without the rendered export or interface, actual clipping, contrast, keyboard operation, and assistive-technology behavior remain untested.

## Keep repairs and conclusions proportional

Name the missing or inaccessible information, the affected surface or operation, and an equivalent way to expose it. A repair might restore a qualification in the print caption, add a meaningful series label, preserve an identifier after reflow, or supply a structured table.

Do not turn a visualization review into an unrequested full application audit. Report an established accessibility obstacle within scope, then identify any consequential test limit. Passing these checks is not a WCAG conformance certification.

## Basis and limits

- [W3C WAI, Complex Images](https://www.w3.org/WAI/tutorials/images/complex/) gives guidance for conveying substantial visual information through text alternatives.
- [WCAG 2.2, Understanding Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) and [Non-text Contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) explain distinct requirements; do not collapse them into one visual judgment.
- [WCAG 2.2, Understanding Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) applies to functionality that must be operated, which needs appropriate implementation evidence.

The inspection matrix and category-key example are original applications. Standards inform relevant checks; actual conformance depends on the full applicable scope and evidence.
