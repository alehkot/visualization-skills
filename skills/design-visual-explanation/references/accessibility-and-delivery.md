# Accessibility and delivery

Use this reference when the explanation needs text alternatives, non-color meaning, interaction, or adaptation to a specified delivery surface. Accessibility requirements shape the information design; implementation and conformance testing still depend on the final medium.

## Define the information that must survive

Identify what the reader must be able to recover: the conclusion, decisive evidence, relationship direction, exceptions, uncertainty, or exact lookup values. Preserve those requirements across the requested formats. Visual similarity between versions is less important than equivalent access to the intended information.

Do not make essential distinctions depend only on color. Combine color with labels, patterns, shapes, position, or another appropriate cue, and verify that the alternative cue actually conveys the distinction. Adding an unexplained symbol does not solve a missing explanation.

Consider a nonvisual reading without pretending that every visual experience has an identical linear equivalent. A relationship list can convey connections; a table can support precise retrieval; a spatial description may need orientation and part-to-whole context. Select the alternative around the same reader task.

## Specify a useful text alternative

For a complex image, plan a concise identification and an accessible fuller explanation where needed. Avoid a long inventory of colors and shapes that omits their meaning. The fuller explanation can use prose, headings, lists, or a table according to the content.

Include the subject and scope, the central relationships or trend, and qualifications necessary to interpret them. Include exact values when lookup or quantitative verification is part of the task. A summary alone may be inadequate for that task; a data table alone may be inadequate when the point is a mechanism or inference.

Do not add conclusions in the alternative text that the source does not support. It should not become a stronger, more certain version of the visual. If surrounding accessible prose already supplies the explanation, identify that association instead of prescribing needless duplication.

## Adapt the information arrangement

| Requested surface | What to preserve | Typical adaptation |
| --- | --- | --- |
| Static image or print | Essential values, conditions, legend, and state | Make hover-only or animated information available directly or in an attached explanation. |
| Monochrome | Category, state, relationship, and emphasis distinctions | Use meaningful labels or redundant visual cues; do not assume different hues remain distinguishable. |
| Narrow view | Entity identity and the comparison or path | Reorganize groups while repeating context where needed; avoid shrinking everything indiscriminately. |
| Text or assistive reading | The same task-relevant facts and relations | Give a deliberate sequence, meaningful headings, and structured values where needed. |
| Interactive exploration | Access to the information exposed by controls | Specify equivalent access for relevant input methods and a way to identify current selection or state. |

Some dense spatial references need a preserved overview plus accessible detail rather than a complete linear rearrangement. Do not require every artifact to fit every device or become a one-column story. Use the actual delivery requirements.

If interaction is proposed, state what it adds. Selection can expose optional detail; animation can show change. Neither should be the sole location of a condition required to interpret the opening claim. Specify a static explanation of essential relationships when static delivery is requested.

Keep technology-specific mechanisms outside the brief unless the user asks for them. “Provide a keyboard-accessible way to inspect each series” states a meaningful requirement. It does not require a particular UI library or guarantee that the future implementation meets it.

## Worked example: an observing-station status explanation

An invented briefing describes three stations: **Hill** is collecting data, **Marsh** is paused for calibration, and **Roof** has not reported a status. The proposed map uses green, amber, and gray dots.

Keep station names and status words available alongside or directly associated with the markers. In the text alternative, preserve the distinction between “paused” and “status unknown”; unknown is not inactive or zero output. If the map's purpose is current status lookup, a corresponding station/status table may carry the essential information.

If the purpose also includes understanding which station lies upstream of another, the table needs that relationship or a supplementary spatial explanation. A list of statuses alone would not provide equivalent information for that different question.

Counterexample to mandatory repetition: if a clearly associated accessible table already gives every relevant status and relationship, do not prescribe a second identical long description solely to fill a template.

## Basis and limits

- [W3C WAI, Complex Images](https://www.w3.org/WAI/tutorials/images/complex/) explains text alternatives for substantial visual information. The exact association mechanism belongs to the delivery technology.
- [WCAG 2.2, Understanding Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) explains why color cannot be the sole visual means of conveying required information.
- [WCAG 2.2, Understanding Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) concerns operation of functionality. Apply it to interactive delivery, not as a demand that a static picture have controls.

The adaptation table and station example are original planning guidance. A brief can specify these needs; accessibility conformance requires evaluation of the actual implementation and applicable criteria.
