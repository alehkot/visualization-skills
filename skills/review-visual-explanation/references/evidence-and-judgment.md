# Evidence and judgment

Use this reference when source coverage is partial, a consequential detail is hard to read, multiple interpretations compete, or the difference between a material finding and a preference is unclear.

## Separate the evidence available for each claim

An artifact can be internally coherent and factually wrong, or factually correct and difficult to read. Record which question a check actually answers.

| Available evidence | Can establish | Does not establish by itself |
| --- | --- | --- |
| Written brief | Specified claims, relationships, labels, intended arrangements | Actual legibility, pixel geometry, interaction, or export behavior. |
| Rendered image or document | Visible marks, text, endpoints, inspected scale and layout | Accuracy against unavailable source data; unseen states or surfaces. |
| Source data or documentation | Agreement with the claims it covers | Agreement of every other claim; accuracy of the source itself. |
| Observed interaction | What happened in the tested state and input path | Behavior of all states, devices, or assistive technologies. |
| Reader-study results | Outcomes for the tested people, tasks, and conditions | Universal comprehension or the cause of every individual error. |

Do not require all evidence types for every review. A source-free chart can still contradict its own scale. A written brief can still reverse a causal relationship. Match the finding to the available evidence rather than broadening the assignment to obtain everything.

## Build and countercheck a finding

1. Locate the exact mark, label, omission, or arrangement. “The diagram is confusing” is not yet a finding.
2. State the evidence: a source passage, an explicit internal contradiction, or a directly observable obstacle to the requested reading task.
3. Explain the consequence. Identify the wrong answer or blocked operation, distinguishing an established inconsistency from a predicted reader response.
4. Check whether the complete artifact resolves the concern. Inspect captions, keys, adjacent prose, supplied variants, and conventions relevant to the stated audience.
5. Propose the smallest repair that removes the established problem without losing useful meaning. Recheck the repair against the source and the other views.

These steps are a reasoning aid, not a required five-part output. One concise paragraph may contain the entire finding.

If competing readings remain, identify the observation that would discriminate between them. Request a clearer view, exact source passage, or missing definition only when it matters. Do not turn uncertainty into a confident correction merely to finish the review.

## Resolve consequential readings

When the verdict depends on a small symbol, decimal, inequality, or arrow endpoint, inspect that detail at a usable scale while retaining enough surrounding context to identify it. A crop can clarify a label but also remove the legend that defines it.

Use available document text or OCR to cross-check difficult rendered text. Reconcile disagreements with the artifact; neither extraction nor an initial visual impression is automatically authoritative. OCR may omit a minus sign, reorder columns, or merge labels. Repeating the same model judgment does not create independent evidence.

Separate “I cannot determine the endpoint at this resolution” from “the connector ends at the wrong node.” The former is an inspection limit. A clear higher-resolution artifact may resolve it without any design change.

Stop when the material concern is resolved or the remaining evidence gap is clear. Do not run every available tool or require two readings of every uncomplicated word.

## Worked example: partial verification

An invented trail map gives distances for three routes and seasonal closure notes. The supplied source is a distance table only.

If the distances match, report that those values agree with the table. Seasonal closures remain unverified; the missing policy does not justify deleting the closure notes or declaring them wrong. If the request concerns distances only, keep the conclusion within that scope.

If the map itself says “All trails open every day” while its legend says “Ridge trail closed on Sundays,” there is an internal contradiction regardless of the missing seasonal source. Identify the two statements and request a reconciled claim based on the actual policy; do not invent which statement is correct.

Counterexample to finding ambiguity everywhere: a plainly associated caption can establish the period for an entire chart. The period need not be repeated inside every mark. A detached screenshot without that caption would be a different inspected artifact.

## Calibrate priority and acceptance

Prioritize wrong decisions, reversed meanings, and concealed decisive conditions above incidental polish. Treat a repair that changes the conclusion differently from one that reduces an avoidable lookup. Labels such as critical or minor are useful only if their consequence is explained; a numerical severity score is not a measurement of harm.

For a material-findings-only request, omit optional stylistic alternatives. Dense expert diagrams, repeated labels, and uniform shapes are not defects solely because another layout is possible. Authoring inconvenience is relevant only if maintainability is in scope or creates an observed communication error.

When no material problem is established, say so and state consequential limits. “No material inconsistency found in the supplied brief; rendered legibility was not inspected” is narrower than certifying the eventual artifact. Do not pad acceptance with fabricated repairs.

## Basis and limits

- [Munzner, A Nested Model for Visualization Design and Validation](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/) separates levels of design and the evidence suited to validating them. It supports keeping different verification claims distinct.
- [Green and Blackwell, Cognitive Dimensions tutorial](https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf) supplies a vocabulary for task-dependent tradeoffs, not a universal defect checklist.

The finding procedure, severity guidance, and trail-map example are original review practices. Passing them does not measure reader comprehension or guarantee factual accuracy.
