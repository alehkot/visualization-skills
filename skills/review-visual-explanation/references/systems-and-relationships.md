# Reviewing systems and relationships

Use this reference when an explanation contains processes, conditional rules, states, dependencies, membership, causality, or feedback. Verify the relationships the artifact actually asserts, not the notation you would have chosen.

## Reconstruct the asserted model

Select a path or connection consequential to the reader's question. Identify its endpoints, direction, relationship type, and condition from the complete artifact. A line might indicate transfer, sequence, dependence, annotation, or simple association. Do not assume that all arrows mean causation.

Compare this reading with the source where available. Keep source statements, visual conventions, and your deductions separate. A familiar rectangle can represent different entity types when explicit labels make those types clear. Similar shapes alone do not establish symbol confusion.

For rendered artifacts, follow a connector through crossings and close spacing to its endpoint. For briefs, review only the connections and arrangements they specify. Unspecified routing is not evidence of a future crossing or false connection.

## Probe the logic with a relevant case

| Inspect | A useful probe | Material mismatch to look for |
| --- | --- | --- |
| Required conditions | Hold one prerequisite absent while the others hold. | The visual allows an outcome the source excludes. |
| Sufficient conditions | Apply the stated condition and inspect what is promised. | A source's possibility or requirement becomes a guarantee. |
| Alternatives and exceptions | Pick an overlapping or exceptional case. | Layout erases the exception or applies it outside its scope. |
| State transitions | Start in a specified state and follow the event or guard. | A drawn transition has the wrong start, condition, or result. |
| Membership | Trace an item with multiple affiliations. | The visual excludes a supported membership or implies exclusivity. |
| Overview/detail views | Follow one entity across the boundary between views. | Its identity, responsibility, or external relationships change silently. |

Use the smallest relevant probe, not an exhaustive simulation of the whole domain. If the source is incomplete, do not add missing branches or claim the diagram lacks a real operation. A set of examples labeled as non-exhaustive is not a complete policy model.

Check exact scope words before alleging an error. “Usually,” “only if,” “at least,” and “after approval” have different consequences. A shortened title can contradict correctly specified branch logic; correct detail does not rescue a false summary.

## Inspect causal and temporal claims

An ordering diagram may establish that one event precedes another without asserting why. A source describing an association does not justify a causal arrow solely because the entities fit a neat story. Conversely, an arrow labeled “reported before” is not a causal overclaim merely because it is directional.

For a causal-loop model, check the meaning of each link's polarity and any delay material to the explanation. Positive does not mean beneficial; a balancing loop does not necessarily act promptly or without oscillation. A closed ring of dependency arrows is not automatically a feedback mechanism.

Require source support for a causal assertion, but distinguish lack of support from disproof. If the artifact labels the link as a hypothesis and preserves competing evidence, the appropriate review may accept that qualification. Do not demand false certainty as the repair.

## Worked example: sequence mistaken for cause

An invented field log records that a park installed lamps in April and that a moth survey counted more moths in June. It supplies no comparison sites or causal analysis. The explanatory brief places the events in two boxes connected by “caused an increase.”

The defect is the asserted causal relationship, not the use of boxes or the horizontal arrangement. A minimal repair is to label the timeline as two reported events, retain the dates, and remove the unsupported causal claim. Do not replace it with “lamps had no effect”; the source does not establish that either.

A control version says “April: lamps installed” and “June: higher count recorded,” joined by a timeline labeled “reported sequence; cause not established.” That version should not receive the same causal finding. If the review asks only about source fidelity, alternative layouts are optional preferences.

## Preserve meaning when repairing structure

Before suggesting a tree, verify that the relation is genuinely single-parent. Before collapsing a group, check whether a required path crosses its boundary. Before deleting a repeated label, check whether it anchors identity in a second view. Before converting a state diagram into a sequence, check whether the task requires possible histories rather than one selected history.

State a repair in terms of the actual affected relationship: relabel a link, restore a condition, reconnect an endpoint, show a second membership, or qualify an assertion. A wholesale redesign is justified only when a smaller repair cannot support the requested task.

## Basis and limits

- [Tversky, Visualizing Thought](https://doi.org/10.1111/j.1756-8765.2010.01113.x) explains how marks and arrangement contribute meanings; that does not make every possible interpretation an observed reader error.
- [C4 notation guidance](https://c4model.com/diagrams/notation) and [arc42's building block view](https://docs.arc42.org/section-5/) illustrate explicit labels and scoped architectural views. Their domain conventions are not mandatory for other diagrams.
- [Cascade Institute's causal-loop handbook](https://cascadeinstitute.org/wp-content/uploads/2024/06/Causal-Loop-Diagrams-Handbook-June-27-2024.pdf) explains qualitative loop conventions, not empirical validation of the reviewed causal account.

The probes and moth-log contrast are original examples of source-based review, not a validated comprehension test.
